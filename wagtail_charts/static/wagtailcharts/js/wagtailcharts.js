/* eslint-disable no-console */
'use strict';

/**
 * Chart.js rendering helper file (hardened)
 * Fixes:
 * - No implicit globals (strict mode + let/const everywhere)
 * - Guards for optional plugins (datalabels / annotation / stacked100)
 * - Safer callback handling (prefers registry over new Function; fallback is try/catch)
 * - Scatter connector plugin validates dataset count/length
 * - Navigator plugin: attaches DOM listeners once (no listener leak), no duplicate handlers
 * - Defensive DOM handling for html legend
 */

/* -----------------------------
 * Global defaults (Chart.js v3+)
 * ----------------------------- */
try {
  if (typeof Chart !== 'undefined' && Chart?.defaults?.set) {
    Chart.defaults.set('plugins.datalabels', { color: '#000000' });
  }
} catch (e) {
  // Non-blocker: defaults API may not exist (e.g. Chart.js v2)
}

/* -----------------------------
 * Formatting utilities
 * ----------------------------- */
function formatValue(val, precision = 1, override) {
  let rawValue;

  if (val && typeof val === 'object' && !Array.isArray(val) && 'y' in val) {
    rawValue = val.y;
  } else {
    rawValue = val;
  }

  if (rawValue === undefined || rawValue === null) return '';

  // If it already contains %, keep it as-is (e.g. "12%")
  const rawStr = String(rawValue);
  if (rawStr.indexOf('%') >= 0) return rawValue;

  // Use locale from window if set; otherwise browser default
  const locale = window.WAGTAILCHARTS_LOCALE;

  // Intl.NumberFormat can handle numeric strings too, but NaN becomes "NaN"
  const asNumber = typeof rawValue === 'number' ? rawValue : Number(rawValue);
  if (Number.isNaN(asNumber)) {
    // Keep original if it isn't a number
    return override ? `${rawStr} ${override}` : rawStr;
  }

  const number = new Intl.NumberFormat(locale, {
    maximumFractionDigits: precision,
  }).format(asNumber);

  if (override !== undefined && override !== '' && override !== null) {
    return `${number} ${override}`;
  }
  return number;
}

function percentageFormatter(val, precision = 1, override) {
  // formatValue already handles % strings safely
  const number = formatValue(val, precision);
  if (override !== undefined && override !== '' && override !== null) {
    return `${number} ${override}`;
  }
  return `${number}%`;
}

function isObject(item) {
  return item && typeof item === 'object' && !Array.isArray(item);
}

function mergeDeep(target, ...sources) {
  if (!sources.length) return target;
  const source = sources.shift();

  if (isObject(target) && isObject(source)) {
    for (const key in source) {
      if (isObject(source[key])) {
        if (!target[key]) Object.assign(target, { [key]: {} });
        mergeDeep(target[key], source[key]);
      } else {
        Object.assign(target, { [key]: source[key] });
      }
    }
  }

  return mergeDeep(target, ...sources);
}

/* -----------------------------
 * HTML Legend plugin
 * ----------------------------- */
function getOrCreateLegendList(chart, id) {
  const legendContainer = document.getElementById(id);
  if (!legendContainer) return null;

  let listContainer = legendContainer.querySelector('ul');

  if (!listContainer) {
    listContainer = document.createElement('ul');
    listContainer.style.display = 'flex';
    listContainer.style.flexDirection = 'row';
    listContainer.style.margin = '0';
    listContainer.style.padding = '0';

    legendContainer.appendChild(listContainer);
  }

  return listContainer;
}

const htmlLegendPlugin = {
  id: 'htmlLegend',
  afterUpdate(chart, args, options) {
    const ul = getOrCreateLegendList(chart, options.containerID);
    if (!ul) return;

    // Remove old legend items
    while (ul.firstChild) ul.firstChild.remove();

    // Reuse the built-in generator (may not exist in older versions)
    const gen = chart?.options?.plugins?.legend?.labels?.generateLabels;
    if (typeof gen !== 'function') return;

    const items = gen(chart);

    items.forEach((item) => {
      const li = document.createElement('li');
      li.style.alignItems = 'center';
      li.style.cursor = 'pointer';
      li.style.display = 'flex';
      li.style.flexDirection = 'row';
      li.style.marginLeft = '10px';

      li.onclick = () => {
        const { type } = chart.config;
        if (type === 'pie' || type === 'doughnut') {
          chart.toggleDataVisibility(item.index);
        } else {
          chart.setDatasetVisibility(
            item.datasetIndex,
            !chart.isDatasetVisible(item.datasetIndex)
          );
        }
        chart.update();
      };

      // Color box
      const boxSpan = document.createElement('span');
      boxSpan.style.background = item.fillStyle;
      boxSpan.style.borderColor = item.strokeStyle;
      boxSpan.style.borderWidth = `${item.lineWidth}px`;
      boxSpan.style.display = 'inline-block';
      boxSpan.style.flexShrink = '0';
      boxSpan.style.height = '20px';
      boxSpan.style.marginRight = '10px';
      boxSpan.style.width = '20px';

      // Text
      const textContainer = document.createElement('p');
      textContainer.style.color = item.fontColor || '';
      textContainer.style.margin = '0';
      textContainer.style.padding = '0';
      textContainer.style.textDecoration = item.hidden ? 'line-through' : '';

      textContainer.appendChild(document.createTextNode(item.text));

      li.appendChild(boxSpan);
      li.appendChild(textContainer);
      ul.appendChild(li);
    });
  },
};

/* -----------------------------
 * Scatter connector plugin (safe)
 * ----------------------------- */
const scatterConnectorPlugin = {
  id: 'connectors',
  afterDatasetsDraw(chart) {
    const ds = chart?.data?.datasets || [];
    if (ds.length < 2) return;

    const firstDs = ds[0];
    const secondDs = ds[1];

    const first = Array.isArray(firstDs?.data) ? firstDs.data : [];
    const second = Array.isArray(secondDs?.data) ? secondDs.data : [];

    if (!first.length || !second.length) return;

    const len = Math.min(first.length, second.length);

    // Use dataset 2 color if available; otherwise fallback to ds[0] backgroundColor; else default
    const bg =
      ds[2]?.backgroundColor ||
      firstDs?.backgroundColor ||
      'rgba(0,0,0,0.35)';

    const firstPointRadius =
      typeof firstDs?.pointRadius === 'number' ? firstDs.pointRadius : 3;
    const secondPointRadius =
      typeof secondDs?.pointRadius === 'number' ? secondDs.pointRadius : 3;

    const ctx = chart.ctx;
    const x = chart.scales.x;
    const y = chart.scales.y;

    if (!ctx || !x || !y) return;

    ctx.save();
    ctx.strokeStyle = bg;
    ctx.lineWidth = 2;

    for (let i = 0; i < len; i++) {
      const p1 = first[i];
      const p2 = second[i];
      if (!p1 || !p2) continue;
      if (p1.x === undefined || p1.y === undefined) continue;
      if (p2.y === undefined) continue;

      const xPix = x.getPixelForValue(p1.x);

      ctx.beginPath();
      ctx.moveTo(xPix, y.getPixelForValue(p1.y) + firstPointRadius);
      ctx.lineTo(xPix, y.getPixelForValue(p2.y) - secondPointRadius);
      ctx.stroke();
    }

    ctx.restore();
  },
};

/* -----------------------------
 * Navigator plugin (no listener leak)
 * ----------------------------- */
const navigatorPlugin = {
  id: 'navigator',
  defaults: {
    handlerH: 30,
    handlerW: 10,
    minDistance: 30,
    xLeft: undefined,
    xRight: undefined,
  },

  afterInit(chart, args, options) {
    // Create per-chart state
    chart.$navigator = chart.$navigator || {
      isDragging: false,
      isHold: false,
      holdTimer: null,
      leftHandler: false,
      rightHandler: false,
      listenersAttached: false,
    };

    const state = chart.$navigator;
    const canvas = chart.canvas;
    if (!canvas || state.listenersAttached) return;

    const holdDuration = 500; // ms

    const getHandlerHalfW = () => (options.handlerW || 10) / 2;

    const isOverLeft = (x) =>
      options.xLeft !== undefined &&
      x >= options.xLeft - getHandlerHalfW() &&
      x <= options.xLeft + getHandlerHalfW();

    const isOverRight = (x) =>
      options.xRight !== undefined &&
      x >= options.xRight - getHandlerHalfW() &&
      x <= options.xRight + getHandlerHalfW();

    const onMouseMove = (e) => {
      if (!chart.chartArea) return;
      const { left, right } = chart.chartArea;

      // Cursor handling
      if (state.isDragging) {
        canvas.style.cursor = 'pointer';
      } else if (isOverLeft(e.offsetX) || isOverRight(e.offsetX)) {
        canvas.style.cursor = 'pointer';
      } else {
        canvas.style.cursor = 'default';
      }

      // Drag handling
      if (!state.isDragging) return;

      const xScale = chart.scales.x;
      const parentChart = chart.$navigatorParent; // set after chart creation
      if (!xScale || !parentChart || typeof parentChart.chartZoom !== 'function')
        return;

      // Keep handles within bounds + min distance
      if (
        state.leftHandler &&
        e.offsetX > left &&
        e.offsetX < options.xRight - options.minDistance
      ) {
        options.xLeft = e.offsetX;
        parentChart.chartZoom(
          xScale.getValueForPixel(options.xLeft),
          xScale.getValueForPixel(options.xRight)
        );
        chart.update('none');
      }

      if (
        state.rightHandler &&
        e.offsetX < right &&
        e.offsetX > options.xLeft + options.minDistance
      ) {
        options.xRight = e.offsetX;
        parentChart.chartZoom(
          xScale.getValueForPixel(options.xLeft),
          xScale.getValueForPixel(options.xRight)
        );
        chart.update('none');
      }
    };

    const onMouseDown = (e) => {
      if (!chart.chartArea) return;

      if (isOverLeft(e.offsetX)) {
        state.isDragging = true;
        state.leftHandler = true;
        state.rightHandler = false;
      } else if (isOverRight(e.offsetX)) {
        state.isDragging = true;
        state.rightHandler = true;
        state.leftHandler = false;
      } else {
        state.isDragging = false;
        state.leftHandler = false;
        state.rightHandler = false;
        return;
      }

      state.isHold = false;
      if (state.holdTimer) clearTimeout(state.holdTimer);
      state.holdTimer = setTimeout(() => {
        state.isHold = true;
      }, holdDuration);
    };

    const onMouseUp = () => {
      if (state.holdTimer) clearTimeout(state.holdTimer);
      state.holdTimer = null;

      state.isDragging = false;
      state.leftHandler = false;
      state.rightHandler = false;
      canvas.style.cursor = 'default';
    };

    const onMouseLeave = () => onMouseUp();

    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseLeave);

    state.listenersAttached = true;
  },

  afterDatasetsDraw(chart, args, options) {
    const { ctx, chartArea } = chart;
    if (!ctx || !chartArea) return;

    const { left, right, height, top } = chartArea;

    if (options.xLeft === undefined) options.xLeft = left;
    if (options.xRight === undefined) options.xRight = right;

    // Selected area background
    ctx.save();
    ctx.beginPath();
    ctx.fillStyle = 'rgba(211, 211, 211, 0.4)';
    ctx.rect(options.xLeft, top, options.xRight - options.xLeft, height);
    ctx.fill();
    ctx.restore();

    // Handlers
    const handlerY = height / 2 + top - options.handlerH / 2;

    function drawHandler(xPos) {
      const middlePos = xPos - options.handlerW / 2;

      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(211, 211, 211, 1)';
      ctx.fillStyle = 'white';
      ctx.lineWidth = 2;
      ctx.rect(middlePos, handlerY, options.handlerW, options.handlerH);
      ctx.fill();
      ctx.stroke();
      ctx.restore();

      ctx.beginPath();
      ctx.strokeStyle = 'rgba(211, 211, 211, 1)';
      ctx.lineWidth = 2;
      ctx.moveTo(xPos, handlerY + 5);
      ctx.lineTo(xPos, handlerY + options.handlerH - 5);
      ctx.stroke();
    }

    drawHandler(options.xLeft);
    drawHandler(options.xRight);
  },
};

/* -----------------------------
 * Callback handling (safe)
 * ----------------------------- */
function resolveConfigCallback(configCallback) {
  if (!configCallback) return null;

  // Preferred: a registry of named callbacks
  // window.WAGTAILCHARTS_CALLBACKS = { myCallback: () => ({...}) }
  const registry = window.WAGTAILCHARTS_CALLBACKS;
  if (registry && typeof registry === 'object' && typeof registry[configCallback] === 'function') {
    return registry[configCallback];
  }

  // Backward-compatible fallback: try to execute provided code (may be blocked by CSP)
  // This is intentionally wrapped in try/catch to avoid crashing charts.
  try {
    // Expecting a function name or callable expression.
    // Example: "myFn" => myFn()
    // Example: "(() => ({plugins:{}}))" => executes it
    const fn = new Function(`return (${configCallback})`)();
    if (typeof fn === 'function') return fn;
  } catch (e) {
    console.warn('Chart callback could not be resolved (likely CSP or invalid code):', e);
  }

  return null;
}

/* -----------------------------
 * Main chart bootstrapping
 * ----------------------------- */
(function renderCharts() {
  const charts = document.querySelectorAll('*[id^="chart-"]');

  for (let i = 0; i < charts.length; i++) {
    const el = charts[i];

    // Defensive parsing
    let parsedDatasets;
    let chartSettings;
    try {
      parsedDatasets = JSON.parse(el.dataset.datasets);
      chartSettings = JSON.parse(el.dataset.config);
    } catch (e) {
      console.error('Invalid chart JSON dataset/config:', e);
      continue;
    }

    const chart_data = parsedDatasets?.data;
    const chart_options = parsedDatasets?.options;
    const chartType = el.dataset.chartType;
    const configCallbackRaw = el.dataset.callback || null;

    if (!chart_data || !chart_options || !chartType) {
      console.warn('Missing chart data/options/type for', el.id);
      continue;
    }

    if (typeof chart_types === 'undefined' || !chart_types[chartType]) {
      console.error('Unknown chart type:', chartType, 'for', el.id);
      continue;
    }

    const chartObj = chart_types[chartType];

    let datasets = [];
    let labels = [];
    const annotations = [];

    if (chartSettings?.column_as_dataset) {
      const titles = chart_options?.title || [];
      for (let index = 0; index < titles.length; index++) {
        const row_title = titles[index];
        if (index !== 0) {
          datasets.push({
            label: row_title,
            data: chart_data[index],
            backgroundColor: chart_options?.color?.[index],
          });
        }
      }
      labels = chart_data[0];
    } else if (chartType === 'scatter') {
      labels = chart_data[0];
      const titles = chart_options?.title || [];

      for (let index = 0; index < titles.length; index++) {
        const row_title = titles[index];
        if (index === 0) continue;

        const xy_data = [];
        for (let label_index = 0; label_index < labels.length; label_index++) {
          const label = labels[label_index];
          xy_data.push({ x: label, y: chart_data[index][label_index] });
        }

        const dataset = {
          label: row_title,
          data: xy_data,
          backgroundColor: chart_options?.color?.[index],
        };

        const pointRadius = chart_options?.point_radius?.[index];
        const pr = parseInt(pointRadius, 10);
        if (!Number.isNaN(pr)) dataset.pointRadius = pr;

        datasets.push(dataset);
      }

      if (Array.isArray(chartSettings?.chart_markers) && chartSettings.chart_markers.length > 0) {
        for (let index = 0; index < chartSettings.chart_markers.length; index++) {
          const marker = chartSettings.chart_markers[index];
          if (!marker?.value) continue;

          annotations.push({
            type: 'line',
            borderColor: marker.value.colour,
            borderWidth: 3,
            borderDash: [6, 4],
            label: {
              backgroundColor: marker.value.colour,
              content: marker.value.label,
              display: true,
              position: 'start',
              yAdjust: parseInt(chartSettings.chart_marker_label_position, 10) || 0,
            },
            scaleID: 'y',
            value: parseFloat(marker.value.value),
          });
        }
      }
    } else {
      datasets = chartObj.render_datasets(chart_data, chart_options);
      labels = chartObj.render_labels(chart_data, chart_options);
    }

    // Right axis?
    const rightAxisEnabled =
      Object.prototype.hasOwnProperty.call(chart_options, 'yaxis') &&
      Array.isArray(chart_options.yaxis) &&
      chart_options.yaxis.includes('right');

    const options = {
      responsive: true,
      elements: {
        point: { pointStyle: 'circle' },
      },
      scales: {
        x: {
          display: true,
          grid: { lineWidth: 0 },
          title: { display: false },
          ticks: {
            callback: function (value, index) {
              const labelStep = parseInt(chartSettings?.x_tick_label_step, 10) || 1;
              return labelStep !== 1
                ? index % labelStep === 0
                  ? this.getLabelForValue(value)
                  : ''
                : this.getLabelForValue(value);
            },
          },
        },
        y: {
          beginAtZero: true,
          display: true,
          position: 'left',
          ticks: {
            callback: function (value) {
              return formatValue(value, chartSettings?.y_left_precision);
            },
          },
          grid: {},
          title: { display: false },
        },
        y1: {
          beginAtZero: true,
          display: false,
          position: 'right',
          ticks: {
            callback: function (value) {
              return formatValue(value, chartSettings?.y_right_precision);
            },
          },
          grid: {},
          title: { display: false },
        },
      },
      plugins: {
        legend: {
          position: chartSettings?.legend_position,
          display: !!chartSettings?.show_legend,
          reverse: !!chartSettings?.reverse_legend,
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.label || '';
              if (label) label += ': ';

              const dataPoint = context.dataset.data[context.dataIndex];

              if (Array.isArray(dataPoint) && dataPoint.length === 2) {
                label += formatValue(
                  (parseFloat(dataPoint[1]) * 1000 - parseFloat(dataPoint[0]) * 1000) / 1000,
                  chartSettings?.precision,
                  chartSettings?.unit_override
                );
              } else {
                label += formatValue(
                  dataPoint,
                  chartSettings?.precision,
                  chartSettings?.unit_override
                );
              }
              return label;
            },
          },
        },
        datalabels: {
          formatter: function (value) {
            if (Array.isArray(value) && value.length === 2) {
              return formatValue(
                (parseFloat(value[1]) * 1000 - parseFloat(value[0]) * 1000) / 1000,
                chartSettings?.precision,
                chartSettings?.unit_override
              );
            }
            return formatValue(value, chartSettings?.precision, chartSettings?.unit_override);
          },
        },
        annotation: {
          annotations: [],
        },
      },
    };

    // Aspect ratio
    if (chartSettings?.aspect_ratio && chartSettings.aspect_ratio !== 'none') {
      options.aspectRatio = Number(chartSettings.aspect_ratio);
    }

    // HTML legend
    if (chartSettings?.html_legend) {
      el.insertAdjacentHTML(
        'afterend',
        `<div id="${el.id.replace('chart', 'chart-legend-container')}"></div>`
      );
      options.plugins.legend.display = false;
      options.plugins.htmlLegend = {
        containerID: el.id.replace('chart', 'chart-legend-container'),
      };
    }

    // Point style
    if (chartSettings?.point_style === 'none') {
      options.elements.point.pointStyle = false;
    } else if (chartSettings?.point_style) {
      options.elements.point.pointStyle = chartSettings.point_style;
    }

    // Title
    if (chartSettings?.chart_title) {
      options.plugins.title = {
        display: true,
        text: chartSettings.chart_title,
        fullSize: false,
        font: { size: 16 },
      };
    }

    // Y settings
    if (chartSettings?.y_left_min !== '') options.scales.y.min = parseFloat(chartSettings.y_left_min);
    if (chartSettings?.y_left_max !== '') options.scales.y.max = parseFloat(chartSettings.y_left_max);
    if (chartSettings?.y_left_step_size !== '') options.scales.y.ticks.stepSize = parseFloat(chartSettings.y_left_step_size);

    if (chartSettings?.y_left_label) {
      options.scales.y.title.display = true;
      options.scales.y.title.text = chartSettings.y_left_label;
    }

    // y left data type
    if (chartSettings?.y_left_data_type === 'percentage') {
      options.scales.y.ticks.callback = function (value) {
        return percentageFormatter(value, chartSettings?.y_left_precision, chartSettings?.unit_override);
      };
      options.plugins.tooltip.callbacks.label = function (context) {
        let label = context.label || '';
        if (label) label += ': ';

        const dataPoint = context.dataset.data[context.dataIndex];
        if (Array.isArray(dataPoint) && dataPoint.length === 2) {
          label += percentageFormatter(
            (parseFloat(dataPoint[1]) * 1000 - parseFloat(dataPoint[0]) * 1000) / 1000,
            chartSettings?.precision,
            chartSettings?.unit_override
          );
        } else {
          label += percentageFormatter(
            dataPoint,
            chartSettings?.precision,
            chartSettings?.unit_override
          );
        }
        return label;
      };

      if (chartSettings?.show_values_on_chart) {
        options.plugins.datalabels.formatter = function (value) {
          return percentageFormatter(value, chartSettings?.precision, chartSettings?.unit_override);
        };
      }
    } else if (chartSettings?.y_left_data_type === 'absolute_number') {
      options.scales.y.ticks.callback = function (value) {
        const unit = chartSettings?.unit_override || '';
        return `${unit}${Math.abs(value).toLocaleString()}`;
      };
      options.plugins.tooltip.callbacks.label = function (context) {
        const unit = chartSettings?.unit_override || '';
        let label = context.label || '';
        if (label) label += ': ';
        const v = context.dataset.data[context.dataIndex];
        return `${label}${unit}${Math.abs(v).toLocaleString()}`;
      };
    }

    // Hide y left
    if (chartSettings?.y_left_show === false) {
      options.scales.y.grid.lineWidth = function (ctx) {
        return ctx.tick && ctx.tick.value === 0 ? 1 : 0;
      };
      options.scales.y.grid.drawBorder = false;
      options.scales.y.ticks.display = false;
    }

    // Right axis settings
    if (rightAxisEnabled) {
      options.scales.y1.display = true;

      if (chartSettings?.y_right_min !== '') options.scales.y1.min = parseFloat(chartSettings.y_right_min);
      if (chartSettings?.y_right_max !== '') options.scales.y1.max = parseFloat(chartSettings.y_right_max);
      if (chartSettings?.y_right_step_size !== '') options.scales.y1.ticks.stepSize = parseFloat(chartSettings.y_right_step_size);

      if (chartSettings?.y_right_label) {
        options.scales.y1.title.display = true;
        options.scales.y1.title.text = chartSettings.y_right_label;
      }

      if (chartSettings?.y_right_data_type === 'percentage') {
        options.scales.y1.ticks.callback = function (value) {
          return percentageFormatter(value, chartSettings?.y_right_precision);
        };

        options.plugins.tooltip.callbacks.label = function (context) {
          let label = context.dataset.label || '';
          if (label) label += ': ';
          if (context.parsed?.y !== null && context.parsed?.y !== undefined) {
            label += percentageFormatter(context.parsed.y, chartSettings?.precision);
          }
          return label;
        };
      }

      // Hide y right
      if (chartSettings?.y_right_show === false) {
        options.scales.y1.grid.lineWidth = function (ctx) {
          return ctx.tick && ctx.tick.value === 0 ? 1 : 0;
        };
        options.scales.y1.grid.drawBorder = false;
        options.scales.y1.ticks.display = false;
      }
    }

    // X label
    if (chartSettings?.x_label) {
      options.scales.x.title.display = true;
      options.scales.x.title.text = chartSettings.x_label;
    }

    // Stacking
    if (chartSettings?.stacking === 'stacked') {
      options.scales.x.stacked = true;
      options.scales.y.stacked = true;
      options.scales.y1.stacked = true;
    }

    // 100% stacking plugin (optional)
    if (chartSettings?.stacking === 'stacked_100') {
      if (typeof window !== 'undefined' && (window.ChartStacked100 || (options.plugins && options.plugins.stacked100))) {
        options.plugins.stacked100 = { enable: true, replaceTooltipLabel: false };
      } else {
        console.warn('stacked_100 requested but stacked100 plugin not detected.');
      }
    }

    // Grid
    if (chartSettings?.show_grid === false) {
      options.scales.x.grid.display = false;
      options.scales.y.grid.lineWidth = function (ctx) {
        return ctx.tick && ctx.tick.value === 0 ? 1 : 0;
      };
      options.scales.y1.grid.lineWidth = function (ctx) {
        return ctx.tick && ctx.tick.value === 0 ? 1 : 0;
      };
    }

    // Pie/doughnut border
    if (chartType === 'pie' || chartType === 'doughnut') {
      options.borderWidth = chartSettings?.pie_border_width;
      options.borderColor = chartSettings?.pie_border_color;
    }

    // Base Chart.js options
    const chartOptions = {
      type: chartObj.chartjs_chart_type,
      data: { labels, datasets },
      plugins: [],
    };

    // Plugins: HTML legend
    if (chartSettings?.html_legend) {
      chartOptions.plugins.push(htmlLegendPlugin);
    }

    // Plugins: Datalabels (optional)
    if (chartSettings?.show_values_on_chart) {
      if (typeof ChartDataLabels !== 'undefined') {
        chartOptions.plugins.push(ChartDataLabels);

        if (chartSettings?.stacking === 'stacked' || chartSettings?.stacking === 'stacked_100') {
          options.plugins.datalabels.formatter = function (value) {
            if (parseFloat(value) === 0.0) return '';
            if (chartSettings?.y_left_data_type === 'percentage') {
              return percentageFormatter(value, chartSettings?.precision, chartSettings?.unit_override);
            }
            return formatValue(value, chartSettings?.precision, chartSettings?.unit_override);
          };
        }
      } else {
        console.warn('show_values_on_chart requested but ChartDataLabels is not loaded.');
      }
    }

    // Horizontal bar handling (prefer indexAxis when available)
    if (chartType === 'bar_horizontal') {
      // If your chart_types maps to a bar chart, Chart.js v3+ supports indexAxis
      chartOptions.options = chartOptions.options || {};
      chartOptions.options.indexAxis = 'y';
    } else if (chartType === 'scatter') {
      options.scales.x.type = 'category';

      if (chartSettings?.scatter_enable_connector) {
        chartOptions.plugins.push(scatterConnectorPlugin);
      }

      if (annotations.length > 0) {
        // Annotation plugin must be loaded externally; otherwise non-blocker
        options.plugins.annotation.annotations = annotations;
      }
    }

    // Merge chart type default options
    chartOptions.options = mergeDeep(options, chartObj.chart_options || {});

    // Apply callback options (safe)
    const cb = resolveConfigCallback(configCallbackRaw);
    if (cb) {
      try {
        const extra = cb();
        chartOptions.options = mergeDeep(chartOptions.options, extra);
      } catch (e) {
        console.warn('Chart callback failed:', e);
      }
    }

    // Create chart
    let myChart;
    try {
      myChart = new Chart(el.getContext('2d'), chartOptions);
    } catch (e) {
      console.error('Failed to create chart for', el.id, e);
      continue;
    }

    // Navigator / mini chart
    const navChartCanvas = document.getElementById(`nav-${el.id}`);
    if (navChartCanvas) {
      // Provide zoom hook
      myChart.chartZoom = function (min, max) {
        this.config.options.scales.x.min = min;
        this.config.options.scales.x.max = max;
        this.update();
      };

      const navChartOptions = JSON.parse(JSON.stringify(chartOptions));
      navChartOptions.options = navChartOptions.options || {};
      navChartOptions.options.aspectRatio = 9;

      if (navChartOptions.options?.scales?.x?.ticks) {
        navChartOptions.options.scales.x.ticks.display = false;
      }

      if (navChartOptions.options?.scales?.y?.title) navChartOptions.options.scales.y.title.text = '';
      if (navChartOptions.options?.scales?.y1?.title) navChartOptions.options.scales.y1.title.text = '';

      if (navChartOptions.options?.plugins?.legend) navChartOptions.options.plugins.legend.display = false;
      if (navChartOptions.options?.plugins?.tooltip) navChartOptions.options.plugins.tooltip.enabled = false;

      navChartOptions.plugins = [navigatorPlugin];

      try {
        const myNavigator = new Chart(navChartCanvas.getContext('2d'), navChartOptions);
        myNavigator.$navigatorParent = myChart; // read by plugin
      } catch (e) {
        console.warn('Failed to create navigator chart for', el.id, e);
      }
    }
  }
})();