document.addEventListener("DOMContentLoaded", () => {
  const dataUrl = window.interactiveTableDataUrl || "/";
  const priority1 = window.interactiveTablePriority1 || "priority1";
  const priority2 = window.interactiveTablePriority2 || "priority2";

  const tbody = document.querySelector("#interactive-table tbody");
  const paginationList = document.getElementById("paginationList");
  const statusDiv = document.getElementById("showstatus");
  const searchInput = document.getElementById("table-search");
  const filterSelects = Array.from(document.querySelectorAll("select[data-filter-name]"));
  const clearBtn = document.getElementById("clear-filters-btn");

  let state = { q: "", page: 1, per_page: 25, filters: {} };
  let debounceTimer = null;

  const showSVG = `<svg class="show_hide__icon" xmlns="http://www.w3.org/2000/svg" width="17" height="11" viewBox="0 0 17 11" fill="none"><path d="M15.7129 0.701355L8.58418 8.70136L0.712891 0.701355" stroke="#082F2A" stroke-width="2"/></svg>`;
  const hideSVG = `<svg class="show_hide__icon" xmlns="http://www.w3.org/2000/svg" width="17" height="11" viewBox="0 0 17 11" fill="none"><path d="M0.746582 9.46259L7.87529 1.46259L15.7466 9.46259" stroke="#082F2A" stroke-width="2"/></svg>`;
  const nextArrowSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 30 30" fill="none"><rect x="30" y="30" width="30" height="30" rx="5" transform="rotate(-180 30 30)" fill="white"/><path d="M12 22L19 15.5L12 9" stroke="#004D44" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const prevArrowSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 30 30" fill="none"><rect width="30" height="30" rx="5" fill="white"/><path d="M18 8L11 14.5L18 21" stroke="#004D44" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

    const urlParams = new URLSearchParams(window.location.search);
    state.page = parseInt(urlParams.get("page")) || 1;


  function formatLabel(str) { return str.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase()); }
  filterSelects.forEach(sel => { state.filters[sel.dataset.filterName] = ""; });

  function buildParams() {
    const params = new URLSearchParams();
    params.set("q", state.q);
    params.set("page", state.page);
    params.set("per_page", state.per_page);
    Object.keys(state.filters).forEach((k, i) => {
      if (state.filters[k]) {
        params.set(`f${i+1}_name`, k);
        params.set(`f${i+1}_val`, state.filters[k]);
      }
    });
    return params;
  }

  function updateStatus(p) {
      const count = p.count || 0;
      const start = count === 0 ? 0 : (p.page - 1) * state.per_page + 1;
      const end = Math.min(p.page * state.per_page, count);

      const activeFilters = Object.entries(state.filters)
        .filter(([_, v]) => v)
        .map(([k, v]) => `${formatLabel(k)}: ${v}`);

      const filterText = activeFilters.length
        ? ` (filtered by ${activeFilters.join(", ")})`
        : "";

      const resultWord = count === 1 ? "result" : "results";

      statusDiv.textContent = `Showing ${start}-${end} of ${count} ${resultWord}${filterText}`;
    }


  function renderRows(rows, otherColumns) {
      tbody.innerHTML = "";

      if (!rows || rows.length === 0) {
        const tr = document.createElement("tr");
        tr.classList.add("no-results-row");
        const td = document.createElement("td");
        td.colSpan = 3;
        td.innerHTML = `<strong>No results found</strong><br>Try adjusting your search or filters above.`;
        tr.appendChild(td);
        tbody.appendChild(tr);
        paginationList.style.display = "none";
        return;
      }

      rows.forEach(row => {
        const detailsId = `details-${row.id}`;
        const toggleId = `toggle-${row.id}`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td headers="col-p1">${row[priority1] ?? ""}</td>
          <td headers="col-p2">${row[priority2] ?? ""}</td>
          <td><button id="${toggleId}" class="toggle-btn" aria-expanded="false" aria-controls="${detailsId}">Show ${showSVG}</button></td>
        `;
        tbody.appendChild(tr);

        const detailsRow = document.createElement("tr");
        detailsRow.hidden = true;
        detailsRow.classList.add("details-row");

        const detailsCell = document.createElement("td");
        detailsCell.colSpan = 3;

        const container = document.createElement("div");
        container.id = detailsId;
        container.classList.add("details-grid");
        container.setAttribute("role", "region");
        container.setAttribute("aria-labelledby", toggleId);

        const validCols = otherColumns.filter(c => row[c]);
        for (let i = 0; i < validCols.length; i += 2) {
          const rowDiv = document.createElement("div");
          rowDiv.classList.add("row");

          const c1 = validCols[i];
          const l1 = document.createElement("div"); l1.className = "label"; l1.textContent = formatLabel(c1);
          const v1 = document.createElement("div"); v1.textContent = row[c1];
          rowDiv.appendChild(l1); rowDiv.appendChild(v1);

          if (validCols[i + 1]) {
            const c2 = validCols[i + 1];
            const l2 = document.createElement("div"); l2.className = "label"; l2.textContent = formatLabel(c2);
            const v2 = document.createElement("div"); v2.textContent = row[c2];
            rowDiv.appendChild(l2); rowDiv.appendChild(v2);
          }

          container.appendChild(rowDiv);
        }

        detailsCell.appendChild(container);
        detailsRow.appendChild(detailsCell);
        tbody.appendChild(detailsRow);

        const btn = tr.querySelector("button");
        btn.addEventListener("click", () => {
          const expanded = btn.getAttribute("aria-expanded") === "true";
          btn.setAttribute("aria-expanded", String(!expanded));
          btn.innerHTML = expanded ? `Show ${showSVG}` : `Hide ${hideSVG}`;
          detailsRow.hidden = expanded;
          btn.focus();
        });
      });
  }

  function renderPagination(p) {
    paginationList.innerHTML = "";

    if (p.has_prev) {
      const liPrev = document.createElement("li");
      liPrev.innerHTML = `<a href="?page=${p.page-1}" class="pagination__link" rel="prev">${prevArrowSVG}</a>`;
      liPrev.querySelector("a").addEventListener("click", handlePageClick);
      paginationList.appendChild(liPrev);
    }

    const liCurr = document.createElement("li");
    liCurr.classList.add("current");
    liCurr.setAttribute("aria-current", "page");
    liCurr.innerHTML = `<a href="#" class="pagination__link pagination__link--active">${p.page}</a>`;
    liCurr.querySelector("a").addEventListener("click", e => e.preventDefault());
    paginationList.appendChild(liCurr);

    if (p.has_next) {
      const liNext = document.createElement("li");
      liNext.innerHTML = `<a href="?page=${p.page+1}" class="pagination__link" rel="next">${nextArrowSVG}</a>`;
      liNext.querySelector("a").addEventListener("click", handlePageClick);
      paginationList.appendChild(liNext);
    }
  }

  function handlePageClick(e) {
    e.preventDefault();
    const page = parseInt(this.getAttribute("href").split("page=")[1]);
    if (!isNaN(page)) {
      state.page = page;
      fetchData();
      history.replaceState(null, "", `?page=${page}`);
    }
  }

  async function fetchData() {
  try {
    statusDiv.textContent = "Loading results…";

    const res = await fetch(dataUrl + "?" + buildParams());
    if (!res.ok) throw new Error("Network error");

    const data = await res.json();

    renderRows(data.rows, data.other_columns);
    renderPagination(data.pagination);
    updateStatus(data.pagination);

  } catch (err) {
    console.error(err);

    const tableDataDiv = document.querySelector(".table-data");

    tbody.innerHTML = "";
    paginationList.innerHTML = "";
    statusDiv.textContent = "";

    tableDataDiv.innerHTML = `
    <div role="alert" class="table-error">
      <div><strong>We couldn’t load the results.</strong></div>
      <div>Please try refreshing the page.</div>
      <button id="reload-page-btn">Refresh page</button>
    </div>
  `;

  document.getElementById("reload-page-btn").addEventListener("click", () => {
    window.location.href = window.location.pathname + "?page=1";
  });
  }
}


  function debouncedFetch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      state.page = 1;
      fetchData();
    }, 250);
  }

  searchInput.addEventListener("input", e => {
    state.q = e.target.value;
    debouncedFetch();
  });

  filterSelects.forEach(sel => sel.addEventListener("change", () => {
    state.filters[sel.dataset.filterName] = sel.value;
    state.page = 1;
    fetchData();
  }));

  clearBtn.addEventListener("click", () => {
      searchInput.value = "";
      state.q = "";
      state.page = 1;
      filterSelects.forEach(sel => { sel.value = ""; state.filters[sel.dataset.filterName] = ""; });

      fetchData();

      const params = new URLSearchParams(window.location.search);
      params.set("page", state.page);
      history.replaceState(null, "", `${window.location.pathname}?${params.toString()}`);
    });

  clearBtn.addEventListener("keypress", e => { if (e.key === "Enter" || e.key === " ") clearBtn.click(); });

  async function populateFilterOptionsOnce() {
      if (!filterSelects.length) return;

      try {
        const res = await fetch(dataUrl + "?page=1&per_page=1000");
        if (!res.ok) throw new Error("Filter fetch failed");

        const data = await res.json();

        filterSelects.forEach(sel => {
          const col = sel.dataset.filterName;
          const values = new Set(data.rows.map(r => r[col]).filter(v => v));
          sel.innerHTML = '<option value="">All</option>';
          Array.from(values).sort().forEach(v => {
            const opt = document.createElement("option");
            opt.value = v;
            opt.textContent = v;
            sel.appendChild(opt);
          });
        });

      } catch (err) {
        await fetchData();
      }
    }

  populateFilterOptionsOnce().then(fetchData);
});
