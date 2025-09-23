
async function init() {
  // Load sql.js
  const SQL = await initSqlJs({
    locateFile: file => `sql-wasm.wasm`  // must match your local wasm file
  });

  // Fetch gzipped DB
  const resp = await fetch("sdn.db.gz");
  const compressed = new Uint8Array(await resp.arrayBuffer());
  const ds = new DecompressionStream("gzip");
  const decompressedStream = new Response(compressed).body.pipeThrough(ds);
  const decompressed = new Uint8Array(await new Response(decompressedStream).arrayBuffer());

  // Create database
  const db = new SQL.Database(decompressed);

  // Hook up search
  const input = document.getElementById("searchBox");
  const resultsDiv = document.getElementById("results");
  const renderVessel = (row) => {
    if (row.vess_flag || row.vess_owner || row.call_sign) {
      return `
      <li>
          <div class="card shadow-sm mt-2">
          <div class="card-body mt-0">
            <h5 class="card-title">Vessel Details</h5>
              <ul class="list-unstyled mb-0">
                  <li><strong>Flag:</strong> ${row.vess_flag || ""}</li>
                  <li><strong>Owner:</strong> ${row.vess_owner || ""}</li>
                  <li><strong>Call Sign:</strong> ${row.call_sign || ""}</li>
              </ul>
            </div>
          </div>
        </li>
      `;
    }
    return "";
  }
  const renderResult = (row) => `
  <div class="card mb-3 shadow-sm">
    <div class="card-body">
      <ul class="list-unstyled mb-2">
        <li><strong>Name:</strong> ${row.sdn_name || ""}</li>
        <li><strong>Title:</strong> ${row.title || ""}</li>
        <li><strong>Program:</strong> ${row.program || ""}</li>
        <li><strong>Remarks:</strong> ${row.remarks || ""}</li>
        ${renderVessel(row)}
      </ul>
    </div>
  </div>
`;

  input.addEventListener("input", () => {
    const rawQuery = input.value.trim();
    resultsDiv.innerHTML = "";
    if (!rawQuery) return;

    // Split query into terms and add '*' for FTS5 prefix search
    const query = rawQuery
      .split(/\s+/)
      .map(term => term + "*")
      .join(" ");

    try {
      const stmt = db.prepare(`
        SELECT sdn_name, program, title, call_sign, vess_flag, vess_owner, remarks
        FROM sdn_fts
        WHERE sdn_fts MATCH ?
        LIMIT 20;
      `);

      stmt.bind([query]);
      while (stmt.step()) {
        const row = stmt.getAsObject();
        const el = document.createElement("div");
        el.className = "result";
        el.innerHTML = renderResult(row);
        resultsDiv.appendChild(el);
      }
      stmt.free();
    } catch (err) {
      resultsDiv.innerHTML = `<div style="color:red">Error: ${err.message}</div>`;
    }
  });
}

init();
