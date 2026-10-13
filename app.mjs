import { evaluateAdultDkaLabs } from './dka_math.mjs';

const form = document.querySelector('#dka-form');
const result = document.querySelector('#result');
const error = document.querySelector('#error');
const output = (name, value) => {
  document.querySelector(`#${['glucose', 'potassium', 'ketones'].includes(name) ? 'out-' : ''}${name}`).textContent = value;
};

function numeric(name, optional = false) {
  const field = form.elements.namedItem(name);
  const raw = field.value.trim();
  if (optional && raw === '') return null;
  if (!raw) throw new RangeError(`Enter ${field.labels?.[0]?.textContent || name}.`);
  const value = Number(raw);
  if (!Number.isFinite(value)) throw new RangeError(`Invalid measurement: ${name}.`);
  return value;
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  error.hidden = true;
  result.hidden = true;
  try {
    const data = evaluateAdultDkaLabs({
      glucose: numeric('glucose'),
      previousGlucose: numeric('previousGlucose', true),
      hours: numeric('hours', true),
      potassium: numeric('potassium'),
      ketones: numeric('ketones'),
      ph: numeric('ph'),
      bicarbonate: numeric('bicarbonate'),
    });
    const status = data.resolutionCriteriaMet
      ? 'Biochemical resolution criteria met on these measurements.'
      : 'Biochemical resolution criteria not met on these measurements.';
    output('resolution', status);
    output('glucose', data.glucoseBelow200
      ? 'Below 200 mg/dL (additional desirable criterion).'
      : 'At or above 200 mg/dL (does not alone determine resolution).');
    output('ketones', data.ketonesBelow06
      ? 'Below 0.6 mmol/L.' : 'At or above 0.6 mmol/L.');
    output('acidbase', data.acidBaseMet
      ? 'Venous pH ≥7.3 or bicarbonate ≥18 mmol/L.'
      : 'Neither venous pH ≥7.3 nor bicarbonate ≥18 mmol/L.');
    output('potassium', data.potassiumStatus);
    output('change', data.glucoseChange === null
      ? 'Not calculated (prior glucose and interval optional).'
      : `${data.glucoseChange.toFixed(1)} mg/dL/hour (${data.glucoseChange >= 0 ? 'falling' : 'rising'}).`);
    const banner = document.querySelector('#out-potassium');
    banner.classList.toggle('danger', data.lowPotassium);
    document.querySelector('#resolution').classList.toggle('caution', !data.resolutionCriteriaMet);
    result.hidden = false;
    document.querySelector('#empty').hidden = true;
  } catch (e) {
    error.textContent = e.message || 'Invalid measurement.';
    error.hidden = false;
  }
});

form.addEventListener('reset', () => {
  result.hidden = true;
  error.hidden = true;
  document.querySelector('#empty').hidden = false;
});
