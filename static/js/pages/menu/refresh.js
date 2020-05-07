const perfEntries = performance.getEntriesByType('navigation');
if (perfEntries.length && perfEntries[0].type == 'back_forward') {
  location.reload();
}