'use strict';

const C = require('./converter.js');

let failed = 0;
let passed = 0;

function assert(cond, msg) {
  if (cond) {
    passed += 1;
  } else {
    failed += 1;
    console.error('FAIL:', msg);
  }
}

function eq(a, b, msg) {
  if (a === b) {
    passed += 1;
  } else {
    failed += 1;
    console.error('FAIL:', msg, '\n  expected:', JSON.stringify(b), '\n  actual:  ', JSON.stringify(a));
  }
}

function cronToCal(input) {
  return C.cronToOnCalendar(input);
}

function calToCron(input) {
  return C.onCalendarToCron(input);
}

// --- Cron → OnCalendar happy path ---
eq(cronToCal('0 4 * * *').output, '*-*-* 04:00:00', 'daily 4am');
eq(cronToCal('0 9 * * 1').output, 'Mon *-*-* 09:00:00', 'monday 9');
eq(cronToCal('0 0 1 * *').output, '*-*-01 00:00:00', 'first of month');
eq(cronToCal('*/15 * * * *').output, '*-*-* *:00/15:00', 'every 15 minutes');
eq(cronToCal('0 * * * *').output, '*-*-* *:00:00', 'hourly from cron');
eq(cronToCal('@hourly').output, '*-*-* *:00:00', '@hourly');
eq(cronToCal('@daily').output, '*-*-* 00:00:00', '@daily');
eq(cronToCal('0 0 * * 0').output, 'Sun *-*-* 00:00:00', 'sunday midnight');
eq(cronToCal('0 0 * * 7').output, 'Sun *-*-* 00:00:00', 'dow 7 is sunday');
eq(cronToCal('0 9 * * MON').output, 'Mon *-*-* 09:00:00', 'named monday');
eq(cronToCal('30 4 1,15 * *').output, '*-*-01,15 04:30:00', '1st and 15th');
eq(cronToCal('0 0 1 1 *').output, '*-01-01 00:00:00', 'yearly');
eq(cronToCal('0 8-17 * * 1-5').output, 'Mon..Fri *-*-* 08..17:00:00', 'weekday work hours');
eq(cronToCal('0,30 * * * *').output, '*-*-* *:00/30:00', 'half hours');
eq(cronToCal('5 4 * * sun').output, 'Sun *-*-* 04:05:00', 'sunday 4:05');
eq(cronToCal('* * * * *').output, '*-*-* *:*:00', 'minutely from cron');
eq(cronToCal('0 0 1 1,4,7,10 *').output, '*-01/3-01 00:00:00', 'quarterly months');
eq(cronToCal('0 20 * * 6,0').output, 'Sat,Sun *-*-* 20:00:00', 'weekends');
eq(cronToCal('1-10/2 * * * *').output, '*-*-* *:01..09/2:00', 'step range minutes');

assert(cronToCal('@hourly').shortcut === 'hourly', '@hourly matches hourly shortcut');
assert(cronToCal('0 0 * * *').shortcut === 'daily', 'midnight matches daily');
assert(cronToCal('0 0 1 * *').shortcut === 'monthly', '1st matches monthly');
assert(cronToCal('0 0 * * 1').shortcut === 'weekly', 'monday midnight is systemd weekly');
assert(cronToCal('@weekly').output === 'Sun *-*-* 00:00:00', 'cron @weekly is Sunday not Monday');

const orCase = cronToCal('30 4 1,15 * 5');
assert(!orCase.representable, 'cron OR is not a single OnCalendar');
assert(orCase.output.includes('OnCalendar=*-*-01,15 04:30:00'), 'OR date line');
assert(orCase.output.includes('OnCalendar=Fri *-*-* 04:30:00'), 'OR weekday line');
assert(/or/i.test(orCase.explanation) || /also every/i.test(orCase.explanation), 'OR explanation');

const reboot = cronToCal('@reboot');
assert(!reboot.ok, '@reboot rejected');
assert(/OnBootSec/.test(reboot.errors.join(' ')), '@reboot mentions OnBootSec');

const badMin = cronToCal('99 4 * * *');
assert(!badMin.ok, 'minute 99 invalid');

const four = cronToCal('0 4 * *');
assert(!four.ok, 'four fields invalid');

const cmd = cronToCal('0 4 * * * /usr/bin/backup');
assert(cmd.ok && cmd.output === '*-*-* 04:00:00', 'trailing command ignored');

// --- OnCalendar → cron happy path ---
eq(calToCron('*-*-* 04:00:00').output, '0 4 * * *', 'cal daily 4am');
eq(calToCron('Mon *-*-* 09:00:00').output, '0 9 * * 1', 'cal monday 9');
eq(calToCron('*-*-01 00:00:00').output, '0 0 1 * *', 'cal first of month');
eq(calToCron('*-*-* *:00/15:00').output, '*/15 * * * *', 'cal every 15');
eq(calToCron('*:0/15').output, '*/15 * * * *', 'short every 15');
eq(calToCron('hourly').output, '0 * * * *', 'hourly shortcut');
eq(calToCron('daily').output, '0 0 * * *', 'daily shortcut');
eq(calToCron('weekly').output, '0 0 * * 1', 'weekly is Monday');
eq(calToCron('monthly').output, '0 0 1 * *', 'monthly shortcut');
eq(calToCron('yearly').output, '0 0 1 1 *', 'yearly shortcut');
eq(calToCron('annually').output, '0 0 1 1 *', 'annually');
eq(calToCron('minutely').output, '* * * * *', 'minutely');
eq(calToCron('quarterly').output, '0 0 1 */3 *', 'quarterly');
eq(calToCron('semiannually').output, '0 0 1 1,7 *', 'semiannually');
eq(calToCron('Mon..Fri *-*-* 09:00:00').output, '0 9 * * 1-5', 'weekday range');
eq(calToCron('Sat,Sun *-*-* 20:00:00').output, '0 20 * * 0,6', 'weekend');
eq(calToCron('*-*-* 4:00:00').output, '0 4 * * *', 'unpadded hour');
eq(calToCron('*-*-* 04:00').output, '0 4 * * *', 'omitted seconds');
eq(calToCron('08:05:00').output, '5 8 * * *', 'time only');
const wedFirst = calToCron('Wed *-1');
assert(wedFirst.ok && !wedFirst.representable, 'Wed *-1 ANDs weekday and date — not standard cron');
eq(calToCron('10-15').output, '0 0 15 10 *', 'month-day only');
eq(calToCron('OnCalendar=*-*-* 04:00:00').output, '0 4 * * *', 'OnCalendar= prefix');
eq(calToCron('mon,fri *-*-* 09:00').output, '0 9 * * 1,5', 'named list');

const manWedTime = calToCron('Wed, 17:48');
eq(manWedTime.output, '48 17 * * 3', 'Wed, 17:48 man page');

const andCase = calToCron('Sat *-*-01..07 00:00:00');
assert(!andCase.representable, 'first Saturday not representable');
assert(!andCase.output, 'no fake cron for AND case');
assert(/AND/i.test(andCase.warnings.join(' ')), 'AND explained');

const secs = calToCron('*-*-* 04:00:30');
assert(!secs.representable, 'non-zero seconds not 5-field cron');

const year = calToCron('2025-*-* 00:00:00');
assert(!year.representable, 'year not in 5-field cron');

const tilde = calToCron('*-02~03');
assert(!tilde.representable, '~ last day not cron');

const tz = calToCron('*-*-* 02:00:00 Europe/Paris');
assert(tz.ok && tz.representable && tz.output === '0 2 * * *', 'timezone still yields cron');
assert(tz.notes.some((n) => /CRON_TZ/.test(n)), 'timezone notes CRON_TZ');

const badCal = calToCron('not a calendar');
assert(!badCal.ok, 'garbage calendar rejected');

// round trips
eq(calToCron(cronToCal('0 4 * * *').output).output, '0 4 * * *', 'round trip 4am');
eq(calToCron(cronToCal('*/15 * * * *').output).output, '*/15 * * * *', 'round trip 15min');
eq(calToCron(cronToCal('0 9 * * 1-5').output).output, '0 9 * * 1-5', 'round trip weekdays');
eq(calToCron(cronToCal('0 0 1 * *').output).output, '0 0 1 * *', 'round trip first');
eq(calToCron(cronToCal('0 20 * * 6,0').output).output, '0 20 * * 0,6', 'round trip weekends');
eq(cronToCal(calToCron('hourly').output).shortcut, 'hourly', 'hourly round trip shortcut');
eq(cronToCal(calToCron('Mon *-*-* 09:00:00').output).output, 'Mon *-*-* 09:00:00', 'monday round trip');

const empty = cronToCal('   ');
assert(empty.empty, 'empty cron');

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
