/**
 * Bidirectional converter between 5-field cron and systemd OnCalendar=.
 *
 * Semantics follow:
 *   - crontab(5) / Vixie cron (Linux man-pages)
 *   - systemd.time(7) calendar events
 *
 * Known non-isomorphisms are surfaced as warnings rather than guessed.
 */
'use strict';

const MINUTE = { min: 0, max: 59, name: 'minute' };
const HOUR = { min: 0, max: 23, name: 'hour' };
const DOM = { min: 1, max: 31, name: 'day-of-month' };
const MONTH = { min: 1, max: 12, name: 'month' };
const DOW = { min: 0, max: 7, name: 'day-of-week' }; // 7 is Sunday in cron
const SECOND = { min: 0, max: 59, name: 'second' };
const YEAR = { min: 1970, max: 2199, name: 'year' };

const MONTH_NAMES = {
  jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6,
  jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12,
};
const MONTH_LABELS = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];
const DOW_NAMES = { sun: 0, mon: 1, tue: 2, wed: 3, thu: 4, fri: 5, sat: 6 };
const DOW_FULL = {
  sunday: 0, monday: 1, tuesday: 2, wednesday: 3,
  thursday: 4, friday: 5, saturday: 6,
};
const DOW_LABELS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const DOW_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const SYSTEMD_DOW_ORDER = [1, 2, 3, 4, 5, 6, 0]; // Mon..Sun

const CRON_MACROS = {
  '@yearly': '0 0 1 1 *',
  '@annually': '0 0 1 1 *',
  '@monthly': '0 0 1 * *',
  '@weekly': '0 0 * * 0', // Sunday — not systemd weekly (Monday)
  '@daily': '0 0 * * *',
  '@midnight': '0 0 * * *',
  '@hourly': '0 * * * *',
};

const SYSTEMD_MACROS = {
  minutely: { seconds: [0], minutes: null, hours: null, days: null, months: null, weekdays: null },
  hourly: { seconds: [0], minutes: [0], hours: null, days: null, months: null, weekdays: null },
  daily: { seconds: [0], minutes: [0], hours: [0], days: null, months: null, weekdays: null },
  monthly: { seconds: [0], minutes: [0], hours: [0], days: [1], months: null, weekdays: null },
  weekly: { seconds: [0], minutes: [0], hours: [0], days: null, months: null, weekdays: [1] },
  yearly: { seconds: [0], minutes: [0], hours: [0], days: [1], months: [1], weekdays: null },
  annually: { seconds: [0], minutes: [0], hours: [0], days: [1], months: [1], weekdays: null },
  quarterly: { seconds: [0], minutes: [0], hours: [0], days: [1], months: [1, 4, 7, 10], weekdays: null },
  semiannually: { seconds: [0], minutes: [0], hours: [0], days: [1], months: [1, 7], weekdays: null },
};

function uniqueSorted(nums) {
  return Array.from(new Set(nums)).sort((a, b) => a - b);
}

function coversAll(values, min, max) {
  if (values.length !== max - min + 1) return false;
  for (let i = min; i <= max; i++) {
    if (values[i - min] !== i) return false;
  }
  return true;
}

function field(values, min, max, extra) {
  const vals = uniqueSorted(values);
  return Object.assign({
    values: vals,
    any: coversAll(vals, min, max),
    star: false,
    tilde: null,
  }, extra || {});
}

function anyField(min, max) {
  const values = [];
  for (let i = min; i <= max; i++) values.push(i);
  return { values, any: true, star: true, tilde: null };
}

function parseInteger(raw, spec) {
  if (!/^\d+$/.test(raw)) {
    throw new Error(`Invalid ${spec.name} value "${raw}".`);
  }
  const n = Number(raw);
  if (n < spec.min || n > spec.max) {
    throw new Error(`${spec.name} ${n} is out of range (${spec.min}–${spec.max}).`);
  }
  return n;
}

function parseNamedOrNumber(raw, spec, names) {
  const key = raw.toLowerCase();
  if (names && names[key] != null) return names[key];
  return parseInteger(raw, spec);
}

/**
 * Parse a Vixie/crontab field: star, N, A-B, star/S, A-B/S, A/S, lists, names.
 * `star` is true if the field begins with `*` (Vixie DOM/DOW OR vs AND rule).
 */
function parseCronField(raw, spec, names) {
  const text = raw.trim();
  if (!text) throw new Error(`Empty ${spec.name} field.`);
  const star = text.startsWith('*');
  const values = [];
  const parts = text.split(',');
  for (const partRaw of parts) {
    const part = partRaw.trim();
    if (!part) throw new Error(`Empty item in ${spec.name} field.`);
    const segs = part.split('/');
    if (segs.length > 2) throw new Error(`Invalid step in ${spec.name} field "${part}".`);
    let step = 1;
    if (segs[1] != null) {
      if (!/^\d+$/.test(segs[1]) || Number(segs[1]) < 1) {
        throw new Error(`Invalid step "${segs[1]}" in ${spec.name}.`);
      }
      step = Number(segs[1]);
    }
    const range = segs[0];
    let start;
    let end;
    if (range === '*') {
      start = spec.min;
      end = spec.max;
    } else if (range.includes('-')) {
      const bounds = range.split('-');
      if (bounds.length !== 2) throw new Error(`Invalid range "${range}" in ${spec.name}.`);
      start = parseNamedOrNumber(bounds[0], spec, names);
      end = parseNamedOrNumber(bounds[1], spec, names);
      if (start > end) {
        throw new Error(
          `Cron ranges cannot wrap: "${range}" in ${spec.name}. Use a list instead (e.g. 5,6,0,1).`,
        );
      }
    } else {
      start = parseNamedOrNumber(range, spec, names);
      end = segs[1] != null ? spec.max : start;
    }
    for (let n = start; n <= end; n += step) values.push(n);
  }
  return field(values, spec.min, spec.max, { star });
}

function normalizeDow(fld) {
  const values = [];
  for (const v of fld.values) {
    values.push(v === 7 ? 0 : v);
  }
  const out = field(values, 0, 6, { star: fld.star });
  return out;
}

function splitCronTokens(input) {
  return input.trim().split(/[\s]+/).filter(Boolean);
}

function looksLikeCommand(token) {
  return /[\/$]|^(?:echo|python|node|bash|sh|perl|ruby|php|curl|wget)/i.test(token);
}

function parseCron(input) {
  const warnings = [];
  let text = input.trim();
  if (!text) return { ok: false, empty: true, errors: [] };

  if (/^@reboot\b/i.test(text)) {
    return {
      ok: false,
      errors: [
        '@reboot is a cron boot event, not a calendar schedule. systemd equivalent is a monotonic timer such as OnBootSec=0, not OnCalendar=.',
      ],
    };
  }

  const macro = text.split(/\s+/)[0].toLowerCase();
  if (CRON_MACROS[macro]) {
    const rest = text.slice(macro.length).trim();
    if (rest && looksLikeCommand(rest.split(/\s+/)[0])) {
      warnings.push('Ignored the command after the cron schedule; converting the 5-field expression only.');
    }
    text = CRON_MACROS[macro];
    if (macro === '@weekly') {
      warnings.push(
        'Cron @weekly is Sunday 00:00 (0 0 * * 0). systemd “weekly” is Monday 00:00. Converted using Sunday.',
      );
    }
  }

  let tokens = splitCronTokens(text);
  if (tokens.length > 5 && tokens.slice(5).some(looksLikeCommand)) {
    warnings.push('Ignored trailing crontab user/command fields; converting the 5-field schedule only.');
    tokens = tokens.slice(0, 5);
  }
  if (tokens.length === 6) {
    return {
      ok: false,
      errors: [
        'Expected 5 cron fields (minute hour day-of-month month day-of-week). A 6th field is ambiguous (seconds in some crons, year in others).',
      ],
    };
  }
  if (tokens.length !== 5) {
    return {
      ok: false,
      errors: [
        `Standard cron has 5 fields; found ${tokens.length}. Example: 0 4 * * *`,
      ],
    };
  }

  try {
    const minutes = parseCronField(tokens[0], MINUTE);
    const hours = parseCronField(tokens[1], HOUR);
    const days = parseCronField(tokens[2], DOM);
    const months = parseCronField(tokens[3], MONTH, MONTH_NAMES);
    const weekdays = normalizeDow(parseCronField(tokens[4], DOW, Object.assign({}, DOW_NAMES, DOW_FULL)));
    const seconds = field([0], 0, 59, { star: false });
    const years = anyField(YEAR.min, YEAR.max);
    years.star = true;

    return {
      ok: true,
      schedule: {
        seconds,
        minutes,
        hours,
        days,
        months,
        weekdays,
        years,
        timezone: null,
        origin: 'cron',
      },
      warnings,
    };
  } catch (err) {
    return { ok: false, errors: [err.message], warnings };
  }
}

function parseSysdPart(raw, spec, opts) {
  const allowTilde = opts && opts.allowTilde;
  const text = raw.trim();
  if (!text) throw new Error(`Empty ${spec.name} component.`);

  let tilde = false;
  let body = text;
  if (body.startsWith('~')) {
    if (!allowTilde) throw new Error(`“~” (last day of month) is not valid in ${spec.name}.`);
    tilde = true;
    body = body.slice(1);
  }

  const segs = body.split('/');
  if (segs.length > 2) throw new Error(`Invalid step in ${spec.name} "${text}".`);
  let step = 1;
  if (segs[1] != null) {
    const stepNum = Number(segs[1]);
    if (!isFinite(stepNum) || stepNum <= 0) {
      throw new Error(`Invalid step "${segs[1]}" in ${spec.name}.`);
    }
    if (spec !== SECOND && !/^\d+$/.test(segs[1])) {
      throw new Error(`Invalid step "${segs[1]}" in ${spec.name}.`);
    }
    step = spec === SECOND ? stepNum : Number(segs[1]);
    if (spec === SECOND && step !== Math.floor(step)) {
      throw new Error('Fractional second steps cannot map to standard cron.');
    }
    if (spec === SECOND) step = Math.floor(stepNum) || stepNum;
  }

  const range = segs[0];
  let start;
  let end;
  let unbounded = false;
  if (range === '*') {
    start = spec.min;
    end = spec.max;
    unbounded = true;
  } else if (range.includes('..')) {
    const bounds = range.split('..');
    if (bounds.length !== 2) throw new Error(`Invalid range "${range}" in ${spec.name}.`);
    start = parseInteger(bounds[0], spec);
    end = parseInteger(bounds[1], spec);
    if (start > end) {
      throw new Error(`Range start is after end in ${spec.name} "${range}".`);
    }
  } else {
    if (spec === SECOND && /^\d+\.\d+$/.test(range)) {
      throw new Error('Fractional seconds have no 5-field cron equivalent.');
    }
    start = parseInteger(range, spec);
    end = segs[1] != null ? spec.max : start;
    unbounded = segs[1] != null;
  }

  const values = [];
  if (spec === SECOND && step !== Math.floor(Number(step))) {
    throw new Error('Fractional second steps cannot map to standard cron.');
  }
  const intStep = Number(step);
  if (intStep < 1 || intStep !== Math.floor(intStep)) {
    throw new Error(`Invalid step in ${spec.name}.`);
  }
  for (let n = start; n <= end; n += intStep) values.push(n);
  return field(values, spec.min, spec.max, {
    star: range === '*',
    tilde: tilde ? start : null,
    unboundedStep: unbounded && segs[1] != null,
  });
}

function parseSysdList(raw, spec, opts) {
  const parts = raw.split(',');
  const fields = parts.map((p) => parseSysdPart(p, spec, opts));
  const values = [];
  let star = false;
  let tilde = null;
  for (const f of fields) {
    values.push.apply(values, f.values);
    if (f.star) star = true;
    if (f.tilde != null) tilde = f.tilde;
  }
  return field(values, spec.min, spec.max, { star, tilde });
}

function parseWeekdayToken(name) {
  const key = name.toLowerCase();
  if (DOW_NAMES[key] != null) return DOW_NAMES[key];
  if (DOW_FULL[key] != null) return DOW_FULL[key];
  return null;
}

function parseWeekdays(expr) {
  const parts = expr.split(',').map((p) => p.trim()).filter(Boolean);
  const values = [];
  for (const part of parts) {
    if (part.includes('..')) {
      const bounds = part.split('..');
      if (bounds.length !== 2) throw new Error(`Invalid weekday range "${part}".`);
      const from = parseWeekdayToken(bounds[0]);
      const to = parseWeekdayToken(bounds[1]);
      if (from == null || to == null) throw new Error(`Unknown weekday in "${part}".`);
      let i = from;
      for (;;) {
        values.push(i);
        if (i === to) break;
        i = (i + 1) % 7;
        if (values.length > 7) break;
      }
    } else {
      const v = parseWeekdayToken(part);
      if (v == null) throw new Error(`Unknown weekday "${part}".`);
      values.push(v);
    }
  }
  return field(values, 0, 6, { star: false });
}

const WEEKDAY_WORD = 'sun(?:day)?|mon(?:day)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|fri(?:day)?|sat(?:urday)?';
const WEEKDAY_PART = `(?:${WEEKDAY_WORD})(?:\\.\\.(?:${WEEKDAY_WORD}))?`;
const WEEKDAYS_HEAD = new RegExp(`^(${WEEKDAY_PART}(?:\\s*,\\s*${WEEKDAY_PART})*),?\\s+`, 'i');
const WEEKDAYS_ONLY = new RegExp(`^(${WEEKDAY_PART}(?:\\s*,\\s*${WEEKDAY_PART})*),?$`, 'i');

function peelWeekdays(text) {
  const only = text.trim().match(WEEKDAYS_ONLY);
  if (only) return { weekdays: parseWeekdays(only[1]), rest: '' };
  const head = text.match(WEEKDAYS_HEAD);
  if (head) return { weekdays: parseWeekdays(head[1]), rest: text.slice(head[0].length).trim() };
  return { weekdays: anyField(0, 6), rest: text };
}

function looksLikeTimezone(token, restHasCalendar) {
  if (!token) return false;
  if (/^(UTC|GMT|Z)$/i.test(token)) return true;
  if (/^[A-Za-z_]+\/[A-Za-z0-9_+\-]+$/.test(token)) return true;
  if (/^[+-]\d{2}(?::?\d{2})?$/.test(token)) return true;
  if (restHasCalendar && /^[A-Za-z][A-Za-z_]+$/.test(token) && parseWeekdayToken(token) == null) {
    return true;
  }
  return false;
}

function splitDateComponents(raw) {
  const chunks = [];
  let buf = '';
  for (let i = 0; i < raw.length; i++) {
    const ch = raw[i];
    const next = raw[i + 1];
    if (ch === '.' && next === '.') {
      buf += '..';
      i++;
      continue;
    }
    if (ch === '-' || ch === '~') {
      if (!buf) throw new Error('Invalid date expression.');
      chunks.push({ value: buf, sepAfter: ch });
      buf = ch === '~' ? '~' : '';
      continue;
    }
    buf += ch;
  }
  if (buf) chunks.push({ value: buf, sepAfter: null });
  return chunks;
}

function parseSysdDate(raw) {
  const chunks = splitDateComponents(raw);
  let yearRaw = '*';
  let monthRaw = '*';
  let dayRaw = '*';
  if (chunks.length === 3) {
    yearRaw = chunks[0].value;
    monthRaw = chunks[1].value;
    dayRaw = chunks[2].value;
  } else if (chunks.length === 2) {
    monthRaw = chunks[0].value;
    dayRaw = chunks[1].value;
  } else if (chunks.length === 1 && chunks[0].value.startsWith('~')) {
    dayRaw = chunks[0].value;
  } else {
    throw new Error(`Unrecognized date "${raw}". Use Year-Month-Day, Month-Day, or *-*-Day.`);
  }
  const years = yearRaw === '*' ? anyField(YEAR.min, YEAR.max) : parseSysdList(yearRaw, YEAR);
  if (yearRaw === '*') years.star = true;
  const months = parseSysdList(monthRaw, MONTH);
  const days = parseSysdList(dayRaw, DOM, { allowTilde: true });
  return { years, months, days };
}

function parseSysdTime(raw) {
  const parts = raw.split(':');
  if (parts.length < 2 || parts.length > 3) {
    throw new Error(`Unrecognized time "${raw}". Use Hour:Minute or Hour:Minute:Second.`);
  }
  const hours = parseSysdList(parts[0], HOUR);
  const minutes = parseSysdList(parts[1], MINUTE);
  const seconds = parts[2] != null ? parseSysdList(parts[2], SECOND) : field([0], 0, 59);
  return { hours, minutes, seconds };
}

function applyMacro(name) {
  const key = name.toLowerCase().replace('semi-annually', 'semiannually');
  const m = SYSTEMD_MACROS[key];
  if (!m) return null;
  return {
    seconds: field(m.seconds, 0, 59),
    minutes: m.minutes ? field(m.minutes, 0, 59) : anyField(0, 59),
    hours: m.hours ? field(m.hours, 0, 23) : anyField(0, 23),
    days: m.days ? field(m.days, 1, 31) : anyField(1, 31),
    months: m.months ? field(m.months, 1, 12) : anyField(1, 12),
    weekdays: m.weekdays ? field(m.weekdays, 0, 6) : anyField(0, 6),
    years: anyField(YEAR.min, YEAR.max),
    timezone: null,
    origin: 'systemd',
    shortcut: key === 'annually' ? 'yearly' : key,
  };
}

function parseOnCalendar(input) {
  const warnings = [];
  let text = input.trim();
  if (!text) return { ok: false, empty: true, errors: [] };
  text = text.replace(/^OnCalendar\s*=\s*/i, '');
  text = text.replace(/^["']|["']$/g, '').trim();
  if (!text) return { ok: false, empty: true, errors: [] };

  try {
    const macroMatch = text.match(
      /^(minutely|hourly|daily|monthly|weekly|yearly|annually|quarterly|semiannually|semi-annually)\b(.*)$/i,
    );
    if (macroMatch) {
      const schedule = applyMacro(macroMatch[1]);
      const tz = macroMatch[2].trim();
      if (tz) {
        if (!looksLikeTimezone(tz, true)) {
          throw new Error(`Unrecognized timezone "${tz}".`);
        }
        schedule.timezone = tz;
      }
      if (schedule.shortcut === 'weekly') {
        warnings.push(
          'systemd “weekly” is Monday 00:00. Cron @weekly is Sunday 00:00. Converted using Monday (0 0 * * 1).',
        );
      }
      return { ok: true, schedule, warnings };
    }

    let timezone = null;
    const tokens = text.split(/\s+/).filter(Boolean);
    if (tokens.length >= 2) {
      const last = tokens[tokens.length - 1];
      const head = tokens.slice(0, -1).join(' ');
      const restHasCalendar = /[:\-]/.test(head) || WEEKDAYS_ONLY.test(head) || WEEKDAYS_HEAD.test(head + ' ');
      if (looksLikeTimezone(last, restHasCalendar)) {
        timezone = last;
        text = head;
      }
    }

    const peeled = peelWeekdays(text);
    let rest = peeled.rest.replace(/T/, ' ').trim();
    const weekdays = peeled.weekdays;
    if (!weekdays.any) weekdays.star = false;
    else weekdays.star = true;

    let years = anyField(YEAR.min, YEAR.max);
    years.star = true;
    let months = anyField(1, 12);
    months.star = true;
    let days = anyField(1, 31);
    days.star = true;
    let hours = field([0], 0, 23);
    let minutes = field([0], 0, 59);
    let seconds = field([0], 0, 59);

    if (rest) {
      const bits = rest.split(/\s+/).filter(Boolean);
      if (bits.length > 2) {
        throw new Error('Too many calendar components. Expected [Weekday] [Date] [Time] [Timezone].');
      }
      if (bits.length === 1) {
        if (bits[0].includes(':')) {
          const t = parseSysdTime(bits[0]);
          hours = t.hours;
          minutes = t.minutes;
          seconds = t.seconds;
        } else {
          const d = parseSysdDate(bits[0]);
          years = d.years;
          months = d.months;
          days = d.days;
        }
      } else if (bits.length === 2) {
        const d = parseSysdDate(bits[0]);
        const t = parseSysdTime(bits[1]);
        years = d.years;
        months = d.months;
        days = d.days;
        hours = t.hours;
        minutes = t.minutes;
        seconds = t.seconds;
      }
    }

    return {
      ok: true,
      schedule: {
        seconds, minutes, hours, days, months, weekdays, years, timezone,
        origin: 'systemd',
      },
      warnings,
    };
  } catch (err) {
    return { ok: false, errors: [err.message], warnings };
  }
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

function compactNumeric(values, min, max, style, kind) {
  if (!values.length) return '';
  if (coversAll(values, min, max)) return '*';
  const fmt = style === 'systemd' ? (n) => pad2(n) : (n) => String(n);
  const rangeSep = style === 'systemd' ? '..' : '-';

  if (values.length === 1) return fmt(values[0]);

  const step = values[1] - values[0];
  let arithmetic = step > 0;
  if (arithmetic) {
    for (let i = 1; i < values.length; i++) {
      if (values[i] !== values[0] + i * step) {
        arithmetic = false;
        break;
      }
    }
  }
  if (arithmetic && step > 1) {
    const last = values[values.length - 1];
    const continuesToEnd = last + step > max;
    const cadenceField = kind === 'minute' || kind === 'hour' || kind === 'second';
    // Avoid “clever” steps like day 1,15 → 1-15/14 or dow 1,5 → 1-6/4.
    const allowStep =
      kind !== 'dow' &&
      (values.length >= 3 || (cadenceField && values[0] === min && continuesToEnd));
    if (allowStep) {
      if (style === 'cron') {
        if (values[0] === min && continuesToEnd) return `*/${step}`;
        if (continuesToEnd) return `${values[0]}-${max}/${step}`;
        return `${values[0]}-${last}/${step}`;
      }
      if (continuesToEnd) return `${fmt(values[0])}/${step}`;
      return `${fmt(values[0])}${rangeSep}${fmt(last)}/${step}`;
    }
  }
  if (arithmetic && step === 1) {
    return `${fmt(values[0])}${rangeSep}${fmt(values[values.length - 1])}`;
  }

  const parts = [];
  let runStart = values[0];
  let prev = values[0];
  for (let i = 1; i <= values.length; i++) {
    const v = values[i];
    if (v === prev + 1) {
      prev = v;
      continue;
    }
    if (prev === runStart) parts.push(fmt(runStart));
    else parts.push(`${fmt(runStart)}${rangeSep}${fmt(prev)}`);
    runStart = v;
    prev = v;
  }
  return parts.join(',');
}

function compactWeekdaysSystemd(values) {
  if (coversAll(values, 0, 6)) return null;
  const set = new Set(values);
  const ordered = SYSTEMD_DOW_ORDER.filter((d) => set.has(d));
  if (!ordered.length) return null;

  const parts = [];
  let i = 0;
  while (i < ordered.length) {
    let j = i;
    while (
      j + 1 < ordered.length &&
      SYSTEMD_DOW_ORDER[(SYSTEMD_DOW_ORDER.indexOf(ordered[j]) + 1) % 7] === ordered[j + 1]
    ) {
      j++;
    }
    if (j - i >= 2) {
      parts.push(`${DOW_SHORT[ordered[i]]}..${DOW_SHORT[ordered[j]]}`);
    } else if (j > i) {
      parts.push(DOW_SHORT[ordered[i]], DOW_SHORT[ordered[j]]);
    } else {
      parts.push(DOW_SHORT[ordered[i]]);
    }
    i = j + 1;
  }
  return parts.join(',');
}

function compactWeekdaysCron(values) {
  if (coversAll(values, 0, 6)) return '*';
  const v = uniqueSorted(values);
  if (v.length === 1) return String(v[0]);
  if (v[v.length - 1] - v[0] === v.length - 1) return `${v[0]}-${v[v.length - 1]}`;
  return v.join(',');
}

function formatOnCalendar(schedule) {
  const y = schedule.years.any || schedule.years.star
    ? '*'
    : compactNumeric(schedule.years.values, YEAR.min, YEAR.max, 'cron', 'year');
  const month = schedule.months.any
    ? '*'
    : compactNumeric(schedule.months.values, 1, 12, 'systemd', 'month');
  const day = schedule.days.tilde != null
    ? `~${pad2(schedule.days.tilde)}`
    : schedule.days.any
      ? '*'
      : compactNumeric(schedule.days.values, 1, 31, 'systemd', 'day');
  const date = `${y}-${month}-${day}`;
  const hh = schedule.hours.any ? '*' : compactNumeric(schedule.hours.values, 0, 23, 'systemd', 'hour');
  const mm = schedule.minutes.any ? '*' : compactNumeric(schedule.minutes.values, 0, 59, 'systemd', 'minute');
  const ss = schedule.seconds.any ? '*' : compactNumeric(schedule.seconds.values, 0, 59, 'systemd', 'second');
  const time = `${hh}:${mm}:${ss}`;
  const wd = schedule.weekdays.any ? '' : compactWeekdaysSystemd(schedule.weekdays.values);
  const bits = [];
  if (wd) bits.push(wd);
  bits.push(date);
  bits.push(time);
  if (schedule.timezone) bits.push(schedule.timezone);
  return bits.join(' ');
}

function formatCron(schedule) {
  const min = schedule.minutes.any ? '*' : compactNumeric(schedule.minutes.values, 0, 59, 'cron', 'minute');
  const hr = schedule.hours.any ? '*' : compactNumeric(schedule.hours.values, 0, 23, 'cron', 'hour');
  const day = schedule.days.any ? '*' : compactNumeric(schedule.days.values, 1, 31, 'cron', 'day');
  const month = schedule.months.any ? '*' : compactNumeric(schedule.months.values, 1, 12, 'cron', 'month');
  const dow = schedule.weekdays.any ? '*' : compactWeekdaysCron(schedule.weekdays.values);
  return `${min} ${hr} ${day} ${month} ${dow}`;
}

function matchingShortcut(schedule) {
  if (schedule.timezone) return null;
  if (schedule.days.tilde != null) return null;
  if (!schedule.years.any && !schedule.years.star) return null;
  const keys = Object.keys(SYSTEMD_MACROS);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    if (key === 'annually') continue;
    const m = applyMacro(key);
    if (
      sameField(schedule.seconds, m.seconds) &&
      sameField(schedule.minutes, m.minutes) &&
      sameField(schedule.hours, m.hours) &&
      sameField(schedule.days, m.days) &&
      sameField(schedule.months, m.months) &&
      sameField(schedule.weekdays, m.weekdays)
    ) {
      return key;
    }
  }
  return null;
}

function sameField(a, b) {
  if (a.any && b.any) return true;
  if (a.any !== b.any) return false;
  if (a.values.length !== b.values.length) return false;
  for (let i = 0; i < a.values.length; i++) {
    if (a.values[i] !== b.values[i]) return false;
  }
  return true;
}

function bothDaysRestricted(schedule, mode) {
  const domRestricted = !schedule.days.any;
  const dowRestricted = !schedule.weekdays.any;
  if (!domRestricted || !dowRestricted) return false;
  if (mode === 'cron') {
    // Vixie: OR only when neither field starts with *
    return !schedule.days.star && !schedule.weekdays.star;
  }
  return true;
}

function joinEnglish(items, conj) {
  const word = conj || 'and';
  if (items.length === 0) return '';
  if (items.length === 1) return items[0];
  if (items.length === 2) return `${items[0]} ${word} ${items[1]}`;
  return `${items.slice(0, -1).join(', ')}, ${word} ${items[items.length - 1]}`;
}

function stepOf(values) {
  if (values.length < 2) return null;
  const step = values[1] - values[0];
  if (step <= 0) return null;
  for (let i = 1; i < values.length; i++) {
    if (values[i] !== values[0] + i * step) return null;
  }
  return step;
}

function describeMinutes(fld) {
  if (fld.any) return 'every minute';
  const step = stepOf(fld.values);
  if (step && fld.values[0] === 0 && fld.values[fld.values.length - 1] + step > 59) {
    if (step === 1) return 'every minute';
    return `every ${step} minutes`;
  }
  if (fld.values.length === 1) return `at minute ${fld.values[0]}`;
  return `at minutes ${joinEnglish(fld.values.map(String))}`;
}

function hhmm(h, m) {
  return `${pad2(h)}:${pad2(m)}`;
}

function describeTime(schedule) {
  if (schedule.seconds.any) {
    return 'every second';
  }
  const secZero = schedule.seconds.values.length === 1 && schedule.seconds.values[0] === 0;
  if (schedule.minutes.any && schedule.hours.any && secZero) {
    return 'every minute';
  }
  if (!schedule.minutes.any && !schedule.hours.any && schedule.hours.values.length === 1 && schedule.minutes.values.length === 1) {
    const t = hhmm(schedule.hours.values[0], schedule.minutes.values[0]);
    if (!secZero) return `at ${t}:${pad2(schedule.seconds.values[0])}`;
    return `at ${t}`;
  }
  if (schedule.hours.any && !schedule.minutes.any) {
    const step = stepOf(schedule.minutes.values);
    if (step && schedule.minutes.values[0] === 0 && schedule.minutes.values[schedule.minutes.values.length - 1] + step > 59) {
      return `every ${step} minutes`;
    }
    if (schedule.minutes.values.length === 1) {
      return `at minute ${schedule.minutes.values[0]} past every hour`;
    }
    return `at minutes ${joinEnglish(schedule.minutes.values.map(String))} past every hour`;
  }
  if (!schedule.hours.any && schedule.minutes.any && secZero) {
    if (schedule.hours.values.length === 1) return `every minute during hour ${schedule.hours.values[0]}`;
    return `every minute during hours ${joinEnglish(schedule.hours.values.map(String))}`;
  }
  if (!schedule.hours.any && !schedule.minutes.any && schedule.minutes.values.length === 1) {
    const m = schedule.minutes.values[0];
    const step = stepOf(schedule.hours.values);
    if (step === 1 && schedule.hours.values.length > 1) {
      const a = schedule.hours.values[0];
      const b = schedule.hours.values[schedule.hours.values.length - 1];
      return `at ${hhmm(a, m)} through ${hhmm(b, m)}`;
    }
    return `at ${joinEnglish(schedule.hours.values.map((h) => hhmm(h, m)))}`;
  }
  return `${describeMinutes(schedule.minutes)}, hours ${schedule.hours.any ? 'every hour' : joinEnglish(schedule.hours.values.map(String))}`;
}

function describeMonths(fld) {
  if (fld.any) return null;
  return joinEnglish(fld.values.map((m) => MONTH_LABELS[m]));
}

function describeDoms(fld) {
  if (fld.tilde != null) {
    if (fld.tilde === 1) return 'the last day of the month';
    return `the ${fld.tilde}rd-to-last day of the month`.replace('2rd', '2nd').replace('3rd-to-last', '3rd-to-last');
  }
  if (fld.any) return null;
  const step = stepOf(fld.values);
  if (step && fld.values[0] === 1 && fld.values[fld.values.length - 1] + step > 31) {
    return `every ${step} days of the month`;
  }
  if (step === 1 && fld.values.length > 2) {
    return `days-of-month ${fld.values[0]} through ${fld.values[fld.values.length - 1]}`;
  }
  if (fld.values.length === 1) {
    const d = fld.values[0];
    const suf = d % 10 === 1 && d !== 11 ? 'st' : d % 10 === 2 && d !== 12 ? 'nd' : d % 10 === 3 && d !== 13 ? 'rd' : 'th';
    return `day-of-month ${d}${suf}`;
  }
  return `days-of-month ${joinEnglish(fld.values.map(String))}`;
}

function describeDows(fld, conj) {
  if (fld.any) return null;
  const set = uniqueSorted(fld.values);
  if (set.length === 5 && sameField(fld, field([1, 2, 3, 4, 5], 0, 6))) return 'Monday through Friday';
  if (set.length === 2 && set[0] === 0 && set[1] === 6) {
    return conj === 'or' ? 'Saturday or Sunday' : 'Saturday and Sunday';
  }
  const step = stepOf(set);
  if (step === 1 && set.length > 1 && !(set[0] === 0 && set[set.length - 1] === 6 && set.length < 7)) {
    return `${DOW_LABELS[set[0]]} through ${DOW_LABELS[set[set.length - 1]]}`;
  }
  return joinEnglish(set.map((d) => DOW_LABELS[d]), conj);
}

function explain(schedule, dialect) {
  const time = describeTime(schedule);
  const months = describeMonths(schedule.months);
  const doms = describeDoms(schedule.days);
  const dows = describeDows(schedule.weekdays);
  const yearPart = schedule.years.any || schedule.years.star
    ? null
    : `in year ${joinEnglish(schedule.years.values.map(String))}`;

  const andDays = dialect === 'systemd' && !schedule.days.any && !schedule.weekdays.any;
  const orDays = dialect === 'cron' && bothDaysRestricted(schedule, 'cron');

  const chunks = [];
  if (time) chunks.push(time.charAt(0).toUpperCase() + time.slice(1));

  if (andDays) {
    chunks.push(`on ${doms}`);
    chunks.push(`only if that date falls on ${describeDows(schedule.weekdays, 'or')}`);
  } else if (orDays) {
    chunks.push(`on ${doms}`);
    chunks.push(`and also every ${dows}`);
  } else {
    if (doms) chunks.push(`on ${doms}`);
    if (dows) chunks.push(`on ${dows}`);
  }
  if (months) chunks.push(`in ${months}`);
  if (yearPart) chunks.push(yearPart);
  if (schedule.timezone) chunks.push(`(${schedule.timezone})`);
  if (!doms && !dows && !months && !yearPart && time && !/^every /i.test(time) && !/every hour/.test(time)) {
    chunks.push('every day');
  }

  let sentence = chunks.join(', ') + '.';
  sentence = sentence.replace('.,', '.');
  return sentence;
}

function cronToOnCalendar(input) {
  const parsed = parseCron(input);
  if (parsed.empty) {
    return { ok: false, empty: true, errors: [], warnings: [], output: '', explanation: '' };
  }
  if (!parsed.ok) {
    return {
      ok: false,
      errors: parsed.errors,
      warnings: parsed.warnings || [],
      output: '',
      explanation: '',
    };
  }
  const schedule = parsed.schedule;
  const warnings = (parsed.warnings || []).slice();
  const notes = [];
  const outputs = [];

  if (bothDaysRestricted(schedule, 'cron')) {
    const dateOnly = Object.assign({}, schedule, { weekdays: anyField(0, 6) });
    dateOnly.weekdays.star = true;
    const dowOnly = Object.assign({}, schedule, { days: anyField(1, 31) });
    dowOnly.days.star = true;
    outputs.push(formatOnCalendar(dateOnly));
    outputs.push(formatOnCalendar(dowOnly));
    warnings.push(
      'Cron ORs day-of-month and day-of-week when both are restricted (neither is *). A single OnCalendar= ANDs them. Use two OnCalendar= lines in the timer unit (systemd ORs multiple OnCalendar= entries).',
    );
    notes.push(
      `Not 1:1 as a single OnCalendar=. Equivalent timer snippet:\nOnCalendar=${outputs[0]}\nOnCalendar=${outputs[1]}`,
    );
    const andForm = formatOnCalendar(schedule);
    notes.push(`A single “${andForm}” would fire only when both the date and weekday match — that is not what this crontab does.`);
    const shortcut = null;
    return {
      ok: true,
      representable: false,
      output: outputs.map((o) => `OnCalendar=${o}`).join('\n'),
      outputs,
      explanation: explain(schedule, 'cron'),
      warnings,
      notes,
      shortcut,
      schedule,
    };
  }

  const formatted = formatOnCalendar(schedule);
  const shortcut = matchingShortcut(schedule);
  if (shortcut) notes.push(`systemd shortcut: ${shortcut}`);
  return {
    ok: true,
    representable: true,
    output: formatted,
    outputs: [formatted],
    explanation: explain(schedule, 'cron'),
    warnings,
    notes,
    shortcut,
    schedule,
  };
}

function onCalendarToCron(input) {
  const parsed = parseOnCalendar(input);
  if (parsed.empty) {
    return { ok: false, empty: true, errors: [], warnings: [], output: '', explanation: '' };
  }
  if (!parsed.ok) {
    return {
      ok: false,
      errors: parsed.errors,
      warnings: parsed.warnings || [],
      output: '',
      explanation: '',
    };
  }
  const schedule = parsed.schedule;
  const warnings = (parsed.warnings || []).slice();
  const notes = [];
  const blockers = [];

  if (schedule.days.tilde != null) {
    blockers.push(
      'systemd “~” means last-N day of the month (e.g. *-02~03 = third-last day of February). Standard 5-field cron has no last-day syntax (some crons offer L or $).',
    );
  }
  if (!schedule.years.any && !schedule.years.star) {
    blockers.push('OnCalendar year filters have no field in standard 5-field cron.');
  }
  if (schedule.seconds.any || schedule.seconds.values.some((s) => s !== 0)) {
    blockers.push(
      'Standard 5-field cron has minute granularity and no seconds field. This OnCalendar fires on a non-zero second (or every second).',
    );
  }
  if (!schedule.days.any && !schedule.weekdays.any) {
    blockers.push(
      'systemd ANDs weekday and date: both must match. Standard cron ORs those fields when both are restricted, so a 5-field expression would run on extra days. Quartz-style “first Saturday” (#) is not Vixie cron.',
    );
  }
  if (schedule.timezone) {
    notes.push(
      `Timezone ${schedule.timezone} is not part of a cron expression. Set CRON_TZ=${schedule.timezone} in the crontab (Vixie/cronie) or run the daemon in that zone.`,
    );
  }

  const shortcut = matchingShortcut(schedule) || schedule.shortcut || null;
  if (shortcut) notes.push(`systemd shortcut: ${shortcut}`);

  if (blockers.length) {
    return {
      ok: true,
      representable: false,
      output: '',
      outputs: [],
      explanation: explain(schedule, 'systemd'),
      warnings: warnings.concat(blockers),
      notes,
      shortcut,
      schedule,
      errors: [],
    };
  }

  const formatted = formatCron(schedule);
  return {
    ok: true,
    representable: true,
    output: formatted,
    outputs: [formatted],
    explanation: explain(schedule, 'systemd'),
    warnings,
    notes,
    shortcut,
    schedule,
  };
}

const PRESETS = [
  {
    id: 'daily-4am',
    label: 'Daily at 4am',
    cron: '0 4 * * *',
    calendar: '*-*-* 04:00:00',
  },
  {
    id: 'monday-9',
    label: 'Every Monday at 9:00',
    cron: '0 9 * * 1',
    calendar: 'Mon *-*-* 09:00:00',
  },
  {
    id: 'hourly',
    label: 'Hourly',
    cron: '0 * * * *',
    calendar: 'hourly',
  },
  {
    id: 'every-15',
    label: 'Every 15 minutes',
    cron: '*/15 * * * *',
    calendar: '*-*-* *:00/15:00',
  },
  {
    id: 'first-of-month',
    label: 'First of the month',
    cron: '0 0 1 * *',
    calendar: '*-*-01 00:00:00',
  },
  {
    id: 'weekdays-9',
    label: 'Weekdays at 09:00',
    cron: '0 9 * * 1-5',
    calendar: 'Mon..Fri *-*-* 09:00:00',
  },
  {
    id: 'weekends-20',
    label: 'Weekends at 20:00',
    cron: '0 20 * * 6,0',
    calendar: 'Sat,Sun *-*-* 20:00:00',
  },
  {
    id: 'sunday-midnight',
    label: 'Every Sunday midnight',
    cron: '0 0 * * 0',
    calendar: 'Sun *-*-* 00:00:00',
  },
  {
    id: 'minutely',
    label: 'Minutely',
    cron: '* * * * *',
    calendar: 'minutely',
  },
  {
    id: 'yearly',
    label: 'Yearly (Jan 1)',
    cron: '0 0 1 1 *',
    calendar: 'yearly',
  },
  {
    id: 'quarterly',
    label: 'Quarterly',
    cron: '0 0 1 1,4,7,10 *',
    calendar: 'quarterly',
  },
  {
    id: 'cron-or',
    label: '1st & 15th plus Fridays',
    cron: '30 4 1,15 * 5',
    calendar: '',
    hint: 'Cron OR → two OnCalendar= lines',
  },
  {
    id: 'first-saturday',
    label: 'First Saturday (systemd AND)',
    cron: '',
    calendar: 'Sat *-*-01..07 00:00:00',
    hint: 'Not a single 5-field cron',
  },
];

const CronSystemd = {
  parseCron,
  parseOnCalendar,
  cronToOnCalendar,
  onCalendarToCron,
  formatCron,
  formatOnCalendar,
  explain,
  PRESETS,
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = CronSystemd;
} else {
  globalThis.CronSystemd = CronSystemd;
}
