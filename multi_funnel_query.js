// Takes a list, returns all subsets of that list (excluding the empty set - [])
// See http://stackoverflow.com/questions/5752002/find-all-possible-subset-combos-in-an-array
function getSubsets(input){
  var allSubsets = [];
  var addSubsets = function(n, input, subset) {
    if (n) {
      _.each(input, function(item, i) {
        addSubsets(n - 1, input.slice(i + 1), subset.concat([item]));
      });
    } else if (subset.length) {
      allSubsets.push(subset);
    }
  }
  _.each(input, function(item, i) {
    addSubsets(i, input, []);
  });
  allSubsets.push(input);
  return allSubsets;
}

// Gets all sub-funnels from a list of events, always including the first and last event
// [A, B, C, D] =>
//   [ [A, D],
//     [A, B, D],
//     [A, C, D],
//     [A, B, C, D] ]
function getFunnels(events) {
  if (events.length <= 2) { // No sub-funnels if there are 2 or less events
    return [events];
  }

  var first = events[0];
  var last = events.slice(-1)[0];
  var rest = events.slice(1, -1);

  var funnels = [[first, last]];
  var subFunnels = getSubsets(rest)

  _.each(subFunnels, function(funnel) {
    funnel = [first].concat(funnel).concat([last]);
    funnels.push(funnel);
  });

  return funnels;
}

var events = [
    'homepage new',
    'Viewed login page',
    'Viewed report',
    'Tutorial Shown',
    'Tutorial Video Started',
    'Tutorial Video Finished',
    'clicked logout link'
];

var funnels = getFunnels(events);

var HOUR  = 60 * 60 * 1000; // in milliseconds
var DAY   = 24 * HOUR;
var WEEK  = 7 * DAY;
var MONTH = 30 * DAY;

var processEvent = function(event, user) {
    if (user) {
        user.state = user.state || { funnels: [] };

        _.each(funnels, function (funnel, funnel_i) {
            user.state.funnels[funnel_i] = user.state.funnels[funnel_i] || [];

            _.each(funnel, function (step, step_i) {
                if (step === event.name && !user.state.funnels[funnel_i][step_i]) {
                    if (step_i === 0) {
                        // We can go ahead and record the first event as soon as we see it
                        user.state.funnels[funnel_i][step_i] = event.time;
                    } else if (user.state.funnels[funnel_i][step_i - 1] && ((user.state.funnels[funnel_i][0].getTime() + HOUR) > event.time.getTime())) {
                        // Otherwise, confirm that we've seen the previous step, and that we haven't gone
                        // too long since the first event in the funnel.
                        user.state.funnels[funnel_i][step_i] = event.time;
                    }
                }
            });
        });
    }
};

var result = {};

_.each(funnels, function (funnel, funnel_i) {
    var funnel_key = funnel.join('|');
    result[funnel_key] = {};
    _.each(funnel, function (step, step_i) {
        result[funnel_key][step_i] = { count: 0 };
    });
});

var processUser = function(user) {
    if (user.state && user.state.funnels && user.state.funnels.length) {
        _.each(funnels, function (funnel, funnel_i) {
            var funnel_key = funnel.join('|');
            _.each(user.state.funnels[funnel_i], function (step, step_i) {
                result[funnel_key][step_i].count++;
            });
        });
    }
};
