/**
 * AUTO-YEET old bulk mail — by Ace, for Ren 🐙
 * Deletes promo/social/forum mail older than 45 days, UNLESS it carries a real
 * content label (Medical, Genetics, Bills, etc.) — same safety net as the manual purge.
 * Sends to Trash (recoverable 30 days), not hard-delete.
 *
 * SETUP (one time):
 *  1. Go to https://script.google.com  -> New project
 *  2. Delete the sample code, paste THIS whole file, click Save (disk icon)
 *  3. Pick function "autoYeetOldBulk" up top -> Run. Authorize when Google asks
 *     (it'll warn "unverified app" because it's YOUR script -> Advanced -> Go to project -> Allow)
 *  4. Click the clock icon (Triggers) -> Add Trigger:
 *        function: autoYeetOldBulk | event source: Time-driven | type: Day timer | 2am-3am
 *  5. Done. It now runs every night and keeps the bulk folders self-cleaning.
 *
 * Tune AGE_DAYS or the label list below anytime.
 */
function autoYeetOldBulk() {
  var AGE_DAYS = 45;
  var BULK = ['Newsletters', 'Social', 'Forums'];           // the auto-expiring buckets
  var PROTECT = ['medical','genetics','bills-and-money','government',
                 'kids-and-school','ai-and-work','receipts-and-orders']; // never delete these

  var bulkQ    = '(' + BULK.map(function(l){ return 'label:' + l; }).join(' OR ') + ')';
  var protectQ = PROTECT.map(function(l){ return '-label:' + l; }).join(' ');
  var query    = bulkQ + ' older_than:' + AGE_DAYS + 'd ' + protectQ;

  var total = 0;
  // batch so we never blow Apps Script quotas; up to ~1500/run, then stop and finish tomorrow
  for (var pass = 0; pass < 5; pass++) {
    var threads = GmailApp.search(query, 0, 300);
    if (threads.length === 0) break;
    for (var i = 0; i < threads.length; i++) { threads[i].moveToTrash(); }
    total += threads.length;
    Utilities.sleep(1000);
  }
  Logger.log('Auto-yeeted ' + total + ' old bulk threads (' + AGE_DAYS + 'd+).');
}
