async function activate() {
  const response = await fetch('explorer.json');
  if (!response.ok) return;
  const { fixture, panel } = await response.json();
  const byId = id => document.getElementById(id);
  function showCase() {
    const arm = document.querySelector('[name="arm"]:checked').value;
    const task = fixture.task_pair[arm];
    const input = task.inputs.at(-1);
    const cert = fixture.expected.certificates[arm];
    byId('input').textContent = input;
    byId('target').textContent = task.outputs.at(-1);
    byId('shortcut').textContent = input.replaceAll('exa','azy');
    const n = cert.complete_one_rule_solutions.length;
    byId('verdict').textContent = (arm === 'CONTROL' ? 'Control' : 'Separation') + ' · ' + n + ' single-rule solution' + (n === 1 ? ' fits' : 's fit') + ' all six demonstrations. Certified minimum length ' + cert.minimum_length + '.';
  }
  function showPanel() {
    const row = panel.find(r => r.model === byId('model').value && r.base_count === byId('base').value);
    byId('counts').textContent = row.primary_family_N + ' families · ' + row.CONTROL_displayed_successes + ' control and ' + row.SEPARATION_displayed_successes + ' separation tasks completed.';
    byId('displayed').textContent = row.displayed_delta_pp_and_95CI.replaceAll('-', '−');
    byId('hidden-pair').textContent = row.unshown_pair_delta_pp_and_95CI.replaceAll('-', '−');
  }
  byId('arms').addEventListener('change',showCase);
  byId('models').addEventListener('change',showPanel);
  showCase(); showPanel();
  byId('arms').hidden = byId('models').hidden = false;
}
activate().catch(() => {});
