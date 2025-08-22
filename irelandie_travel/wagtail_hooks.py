from wagtail import hooks

@hooks.register("insert_editor_js")
def editor_js():
    return """
<script>
(function() {
  let lastSelectedValues = [];

  function updateChoices(container) {
    const allSelects = container.querySelectorAll('.unique-choice-block select');

    // Clear values of deleted selects
    allSelects.forEach(select => {
      const blockEl = select.closest('.sequence-member');
      const deletedInput = blockEl?.querySelector('input[name$="-deleted"]');
      if (deletedInput?.value === "1") {
        select.value = "";
      }
    });

    // Get active (non-deleted) selects
    const activeSelects = Array.from(allSelects).filter(select => {
      const blockEl = select.closest('.sequence-member');
      const deletedInput = blockEl?.querySelector('input[name$="-deleted"]');
      return deletedInput?.value !== "1";
    });

    // Collect selected values from active selects
    const selectedValues = activeSelects.map(s => s.value).filter(v => v);

    // Update options in all selects
    allSelects.forEach(select => {
      const blockEl = select.closest('.sequence-member');
      const deletedInput = blockEl?.querySelector('input[name$="-deleted"]');
      const isDeleted = deletedInput?.value === "1";

      Array.from(select.options).forEach(opt => {
        if (!isDeleted) {
          opt.disabled = selectedValues.includes(opt.value) && opt.value !== select.value;
        } else {
          opt.disabled = true;
        }
      });
    });

    lastSelectedValues = selectedValues;
  }

  // Listen for select changes
  document.addEventListener("change", function(e) {
    if (e.target.closest('.unique-choice-block')) {
      updateChoices(document);
    }
  });

  // Observe DOM mutations
  const observer = new MutationObserver(function(mutations) {
    let changed = false;

    mutations.forEach(m => {
      if (m.type === "childList" && (m.addedNodes.length || m.removedNodes.length)) {
        changed = true;
      }

      if (m.type === "attributes" && m.target.tagName === "INPUT" && m.target.name.endsWith("-deleted")) {
        if (m.target.value === "1") {
          // Clear the corresponding select
          const baseName = m.target.name.replace(/-deleted$/, "");
          const selectName = baseName + "-value-travel_caution_level";
          const select = document.querySelector(`select[name="${selectName}"]`);
          if (select) select.value = "";
        }
        changed = true;
      }
    });

    if (changed) updateChoices(document);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["value"]
  });

  // Initial run on DOM load
  document.addEventListener("DOMContentLoaded", function() {
    updateChoices(document);
  });
})();
</script>
    """
