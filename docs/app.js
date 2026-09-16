(async function () {
  const $ = (selector) => document.querySelector(selector);
  let issues = [];
  const text = (value) => String(value ?? "Unavailable");
  const formatDate = (value) => value ? new Date(value).toLocaleString() : "Unavailable";
  const escapeHtml = (value) => text(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));

  function renderBars(selector, values) {
    const element = $(selector);
    const entries = Object.entries(values || {});
    const max = Math.max(1, ...entries.map((entry) => entry[1]));
    element.innerHTML = entries.length ? entries.map(([name, count]) =>
      `<div class="bar-row"><span>${escapeHtml(name)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.round(count / max * 100)}%"></div></div><strong>${count}</strong></div>`
    ).join("") : '<span class="muted">No analyzed Issues</span>';
  }

  function reportSummary(report) {
    const summary = report.summary || {};
    $("#last-analysis").textContent = formatDate(report.generated_at || report.last_analysis);
    $("#issues-analyzed").textContent = report.total_issues ?? summary.issues_analyzed ?? 0;
    $("#high-priority").textContent = report.high_priority_count ?? 0;
    $("#urgent").textContent = report.urgent_count ?? 0;
    $("#human-review").textContent = report.human_review_count ?? summary.human_review_required ?? 0;
    renderBars("#categories", report.category_summary || report.distributions?.categories);
    renderBars("#priorities", report.priority_summary || report.distributions?.priorities);
    renderBars("#sentiments", report.sentiment_summary || report.distributions?.sentiments);
    renderBars("#teams", report.team_summary || report.distributions?.teams);
  }

  function showDetail(issue) {
    $("#detail-title").textContent = issue.title || issue.issue_label || "Issue";
    const references = (issue.similar_issues || issue.similar_tickets || []).map((item) => `${escapeHtml(item.reference_id)} (${item.score ?? "n/a"})`).join(", ") || "None";
    $("#detail-content").innerHTML = `<div class="detail-grid"><div><span>Category</span><strong>${escapeHtml(issue.category)}</strong></div><div><span>Priority</span><strong>${escapeHtml(issue.priority)}</strong></div><div><span>Sentiment</span><strong>${escapeHtml(issue.sentiment)}</strong></div><div><span>Confidence</span><strong>${Math.round((issue.confidence || 0) * 100)}%</strong></div><div><span>Recommended team</span><strong>${escapeHtml(issue.recommended_team)}</strong></div><div><span>Human review</span><strong>${issue.human_review_required ? "Required" : "Not required"}</strong></div></div><p><strong>Similar references:</strong> ${references}</p><p><strong>Review reason:</strong> ${escapeHtml((issue.review_reasons || []).join(", ") || "None recorded")}</p><div class="draft"><strong>Response draft</strong><p>${escapeHtml(issue.suggested_response || "Insufficient evidence.")}</p></div>${issue.url ? `<a class="issue-link" href="${escapeHtml(issue.url)}" target="_blank" rel="noopener">Open public GitHub Issue ↗</a>` : ""}`;
    $("#detail").hidden = false;
    $("#detail").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderTable() {
    const query = $("#search").value.trim().toLowerCase();
    const priority = $("#priority-filter").value;
    const review = $("#review-filter").value;
    const filtered = issues.filter((issue) => {
      const haystack = `${issue.title || ""} ${issue.category || ""} ${issue.recommended_team || ""}`.toLowerCase();
      return (!query || haystack.includes(query)) && (!priority || issue.priority === priority) && (!review || String(Boolean(issue.human_review_required)) === review);
    });
    $("#result-count").textContent = `${filtered.length} of ${issues.length}`;
    $("#empty").hidden = filtered.length !== 0;
    $("#issues").innerHTML = filtered.map((issue, index) => `<tr tabindex="0" data-index="${issues.indexOf(issue)}"><td>${escapeHtml(issue.issue_label || `Issue #${issue.issue_number}`)}</td><td class="title-cell">${escapeHtml(issue.title || "Untitled issue")}</td><td>${escapeHtml(issue.category)}</td><td><span class="tag ${issue.priority === "urgent" || issue.priority === "high" ? "warn" : ""}">${escapeHtml(issue.priority)}</span></td><td>${escapeHtml(issue.sentiment)}</td><td>${Math.round((issue.confidence || 0) * 100)}%</td><td>${escapeHtml(issue.recommended_team)}</td><td>${issue.human_review_required ? '<span class="tag warn">Required</span>' : "No"}</td></tr>`).join("");
    document.querySelectorAll("#issues tr").forEach((row) => { row.addEventListener("click", () => showDetail(issues[Number(row.dataset.index)])); row.addEventListener("keydown", (event) => { if (event.key === "Enter") row.click(); }); });
  }

  $("#search").addEventListener("input", renderTable);
  $("#priority-filter").addEventListener("change", renderTable);
  $("#review-filter").addEventListener("change", renderTable);
  $("#close-detail").addEventListener("click", () => { $("#detail").hidden = true; });
  try {
    const response = await fetch("./report.json", { cache: "no-store" });
    if (!response.ok) throw new Error("report unavailable");
    const report = await response.json();
    reportSummary(report);
    issues = report.issues || report.results || [];
    renderTable();
  } catch (error) {
    $("#error").hidden = false;
    reportSummary({ summary: {}, distributions: {}, results: [] });
    renderTable();
  }
}());
