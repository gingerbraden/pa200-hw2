// Taskboard — minimal JS enhancements

// Auto-focus the title field on page load
document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("title");
  if (titleInput) titleInput.focus();

  // Animate progress bar on load
  const fill = document.querySelector(".progress-fill");
  if (fill) {
    const target = fill.style.width;
    fill.style.width = "0%";
    requestAnimationFrame(() => {
      setTimeout(() => { fill.style.width = target; }, 80);
    });
  }

  // Keyboard shortcut: N to focus new task input
  document.addEventListener("keydown", (e) => {
    if (e.key === "n" && !["INPUT","TEXTAREA"].includes(document.activeElement.tagName)) {
      const t = document.getElementById("title");
      if (t) { t.focus(); e.preventDefault(); }
    }
  });
});
