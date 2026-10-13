// Adult DKA laboratory monitoring (2024 consensus, doi:10.2337/dci24-0032).
// Research/education only. Never generates medication orders or pump commands.

export function measurement(name, value, min, max) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) {
    throw new RangeError(`${name} must be a finite number between ${min} and ${max}.`);
  }
  return value;
}

export function evaluateAdultDkaLabs(values) {
  const glucose = measurement('Current glucose', values.glucose, 0, 2000);
  const potassium = measurement('Potassium', values.potassium, 0, 15);
  const ketones = measurement('Blood beta-hydroxybutyrate', values.ketones, 0, 30);
  const ph = measurement('Venous pH', values.ph, 6, 8);
  const bicarbonate = measurement('Bicarbonate', values.bicarbonate, 0, 60);
  const hasPrior = values.previousGlucose !== null && values.previousGlucose !== undefined;
  const hasHours = values.hours !== null && values.hours !== undefined;
  if (hasPrior !== hasHours) {
    throw new RangeError('Enter both previous glucose and elapsed hours, or leave both blank.');
  }
  let glucoseChange = null;
  if (hasPrior) {
    const previous = measurement('Previous glucose', values.previousGlucose, 0, 2000);
    const hours = measurement('Elapsed hours', values.hours, 0, 168);
    if (hours === 0) throw new RangeError('Elapsed hours must be greater than zero.');
    glucoseChange = (previous - glucose) / hours;
  }
  const acidBaseMet = ph >= 7.3 || bicarbonate >= 18;
  const lowPotassium = potassium < 3.5;
  return {
    glucoseChange,
    glucoseBelow200: glucose < 200,
    ketonesBelow06: ketones < 0.6,
    acidBaseMet,
    resolutionCriteriaMet: ketones < 0.6 && acidBaseMet,
    lowPotassium,
    potassiumStatus: lowPotassium
      ? 'LOW — clinician assessment is required before insulin treatment.'
      : potassium > 5
      ? 'Above 5.0 mmol/L — requires monitoring and clinician review.'
      : '3.5–5.0 mmol/L — continue clinician-directed monitoring.',
  };
}
