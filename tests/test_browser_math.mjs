import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluateAdultDkaLabs } from '../dka_math.mjs';

const baseline = {
  glucose: 190, potassium: 4, ketones: 0.5, ph: 7.31, bicarbonate: 17,
  previousGlucose: null, hours: null,
};
const calculate = (patch = {}) => evaluateAdultDkaLabs({ ...baseline, ...patch });

test('resolution requires ketones and an acid-base criterion', () => {
  assert.equal(calculate().resolutionCriteriaMet, true);
  assert.equal(calculate({ ph: 7.2, bicarbonate: 18 }).resolutionCriteriaMet, true);
  assert.equal(calculate({ ketones: 0.6 }).resolutionCriteriaMet, false);
  assert.equal(calculate({ ph: 7.29, bicarbonate: 17.99 }).resolutionCriteriaMet, false);
});

test('glucose alone does not establish resolution', () => {
  assert.equal(calculate({ glucose: 300 }).resolutionCriteriaMet, true);
  assert.equal(calculate({ glucose: 99, ketones: 4 }).resolutionCriteriaMet, false);
});

test('potassium safety cutoff is strictly less than 3.5', () => {
  assert.equal(calculate({ potassium: 3.49 }).lowPotassium, true);
  assert.equal(calculate({ potassium: 3.5 }).lowPotassium, false);
});

test('glucose velocity signed by direction and duration', () => {
  assert.equal(calculate({ glucose: 200, previousGlucose: 310, hours: 2 }).glucoseChange, 55);
  assert.equal(calculate({ glucose: 310, previousGlucose: 200, hours: 2 }).glucoseChange, -55);
  assert.equal(calculate().glucoseChange, null);
});

test('unpaired, non-finite, out-of-range and zero elapsed hours rejected', () => {
  for (const value of [
    { glucose: NaN }, { potassium: Infinity }, { ketones: -1 },
    { previousGlucose: 300 }, { hours: 2 }, { previousGlucose: 300, hours: 0 },
    { ph: 9 }, { bicarbonate: -2 },
  ]) assert.throws(() => calculate(value), RangeError);
});
