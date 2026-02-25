/*!
 * chartjs-plugin-stacked100 (hardened build)
 * - Safer global detection (globalThis fallback)
 * - Does not assume options.scales exists
 * - Wraps tooltip callback instead of clobbering
 * - More defensive cloning + dataset checks
 */

(function (root, factory) {
  if (typeof exports === "object" && typeof module === "object") {
    module.exports = factory();
  } else if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof exports === "object") {
    exports.ChartjsPluginStacked100 = factory();
  } else {
    root.ChartjsPluginStacked100 = factory();
  }
})(
  (typeof globalThis !== "undefined" && globalThis) ||
    (typeof window !== "undefined" && window) ||
    (typeof self !== "undefined" && self) ||
    (typeof global !== "undefined" && global) ||
    this,
  function () {
    "use strict";

    function isPlainObject(x) {
      return x && typeof x === "object" && !Array.isArray(x);
    }

    function getValue(point, isHorizontal) {
      // point can be number | string | {x,y}
      if (isPlainObject(point)) {
        return isHorizontal ? point.x : point.y;
      }
      return point;
    }

    function clampPrecision(p) {
      // default 1, allow [0..16]
      if (p === undefined || p === null) return 1;
      var n = Math.floor(p);
      if (isNaN(n) || n < 0 || n > 16) return 1;
      return n;
    }

    function roundPercent(v, precision) {
      var e = Math.pow(10, precision);
      return Math.round(v * e) / e;
    }

    function shallowCloneDataArray(arr) {
      // Works for numeric arrays; for objects it clones the object references (OK for this plugin)
      if (!Array.isArray(arr)) return [];
      return arr.slice();
    }

    function snapshotOriginalData(chartData) {
      // Save a snapshot of original dataset.data arrays
      chartData.originalData = (chartData.datasets || []).map(function (ds) {
        return shallowCloneDataArray(ds && ds.data);
      });
    }

    function restoreOriginalData(chartData) {
      if (!chartData || !Array.isArray(chartData.originalData)) return;
      chartData.originalData.forEach(function (arr, idx) {
        if (chartData.datasets[idx]) chartData.datasets[idx].data = arr;
      });
    }

    function applyCalculatedData(chartData) {
      if (!chartData || !Array.isArray(chartData.calculatedData)) return;
      chartData.calculatedData.forEach(function (arr, idx) {
        if (chartData.datasets[idx]) chartData.datasets[idx].data = arr;
      });
    }

    function hasNegativeValues(chartData, isHorizontal) {
      var dsets = chartData.datasets || [];
      for (var i = 0; i < dsets.length; i++) {
        var ds = dsets[i];
        var data = (ds && ds.data) || [];
        for (var j = 0; j < data.length; j++) {
          var v = Number(getValue(data[j], isHorizontal));
          if (!isNaN(v) && v < 0) return true;
        }
      }
      return false;
    }

    function computeTotalsByIndexAndStack(chartData, isHorizontal) {
      var dsets = chartData.datasets || [];
      var len = 0;
      if (dsets[0] && Array.isArray(dsets[0].data)) len = dsets[0].data.length;

      // visible flags
      var visible = dsets.map(function (ds) {
        return ds && ds.hidden ? 0 : 1;
      });

      var totals = new Array(len);
      for (var i = 0; i < len; i++) totals[i] = {};

      for (var di = 0; di < dsets.length; di++) {
        var ds = dsets[di] || {};
        var stackKey = ds.stack || "__default__";
        var data = ds.data || [];

        for (var idx = 0; idx < len; idx++) {
          var v = Number(getValue(data[idx], isHorizontal));
          if (isNaN(v)) v = 0;

          if (!totals[idx][stackKey]) totals[idx][stackKey] = 0;
          totals[idx][stackKey] += Math.abs(v) * visible[di];
        }
      }

      return totals;
    }

    function calculatePercentData(chartData, isHorizontal, precision) {
      var dsets = chartData.datasets || [];
      var totals = computeTotalsByIndexAndStack(chartData, isHorizontal);

      return dsets.map(function (ds) {
        ds = ds || {};
        var stackKey = ds.stack || "__default__";
        var data = ds.data || [];

        return (data || []).map(function (pt, idx) {
          var denom = totals[idx] ? totals[idx][stackKey] : 0;
          var raw = Number(getValue(pt, isHorizontal));
          if (isNaN(raw)) raw = 0;

          if (!raw || !denom) return 0;

          var pct = (100 * raw) / denom;
          return roundPercent(pct, precision);
        });
      });
    }

    function ensureScales(options) {
      options.scales = options.scales || {};
      options.scales.x = options.scales.x || {};
      options.scales.y = options.scales.y || {};
      return options.scales;
    }

    function isHorizontalChart(chart) {
      return chart && chart.options && chart.options.indexAxis === "y";
    }

    var stacked100Plugin = {
      id: "stacked100",

      beforeInit: function (chart, _args, pluginOpts) {
        if (!pluginOpts || !pluginOpts.enable) return;

        var opts = chart.options || (chart.options = {});
        var scales = ensureScales(opts);

        // Always stacked
        scales.x.stacked = true;
        scales.y.stacked = true;

        var horizontal = isHorizontalChart(chart);
        var valueAxis = horizontal ? "x" : "y";

        var neg = hasNegativeValues(chart.data, horizontal);
        scales[valueAxis].min = neg ? -100 : 0;
        scales[valueAxis].max = 100;

        // Tooltip label wrapping (optional)
        var replace = pluginOpts.replaceTooltipLabel;
        var shouldReplace = replace === undefined ? true : !!replace;

        if (shouldReplace) {
          opts.plugins = opts.plugins || {};
          opts.plugins.tooltip = opts.plugins.tooltip || {};
          opts.plugins.tooltip.callbacks = opts.plugins.tooltip.callbacks || {};

          var prevLabel = opts.plugins.tooltip.callbacks.label;

          opts.plugins.tooltip.callbacks.label = function (context) {
            try {
              var data = context.chart.data;
              var dsIndex = context.datasetIndex;
              var i = context.dataIndex;

              var dsLabel =
                (data.datasets &&
                  data.datasets[dsIndex] &&
                  data.datasets[dsIndex].label) ||
                "";

              var raw =
                data.originalData &&
                data.originalData[dsIndex] &&
                data.originalData[dsIndex][i];

              var pct =
                data.calculatedData &&
                data.calculatedData[dsIndex] &&
                data.calculatedData[dsIndex][i];

              // Keep existing callback if it exists
              if (typeof prevLabel === "function") {
                // if previous is an array of labels, Chart.js accepts arrays too
                // but we’ll still return our single string if it returns non-string.
                prevLabel(context);
              }

              return dsLabel + ": " + pct + "% (" + getValue(raw, horizontal) + ")";
            } catch (e) {
              // Fallback to previous callback if ours fails
              if (typeof prevLabel === "function") return prevLabel(context);
              return "";
            }
          };
        }
      },

      beforeUpdate: function (chart, _args, pluginOpts) {
        if (!pluginOpts || !pluginOpts.enable) return;

        var data = chart.data || (chart.data = {});
        snapshotOriginalData(data);

        var precision = clampPrecision(pluginOpts.precision);
        var horizontal = isHorizontalChart(chart);

        data.calculatedData = calculatePercentData(data, horizontal, precision);
        applyCalculatedData(data);
      },

      afterUpdate: function (chart, _args, pluginOpts) {
        if (!pluginOpts || !pluginOpts.enable) return;
        restoreOriginalData(chart.data);
      },
    };

    return stacked100Plugin;
  }
);