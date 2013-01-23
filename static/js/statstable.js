/*

// HittingTable
data = [
	{name: 'Matt Kemp',
	 player_id: 12345,
	 tnpl_team: 'Pinetar',
	 tnpl_team_id: 2,
	 tnpl_salary: 2.50,
	 BA: 0.330,
	 AB: 660,
	 BA_dollar: 1.6,
	 R: 101,
	 R_dollar: 2.6,
	 HR: 39,
	 HR_dollar: 2.59,
	 RBI: 160,
	 RBI_dollar: 3.9,
	 SB: 40,
	 SB_dollar: 2.57,
	 POS: 'OF',
	 POS_dollar: 5.51},
	...
];

// PitchingTable
data = [
	{name: 'Roy Halladay',
	 player_id: 12345,
	 tnpl_team: 'Pinetar',
	 tnpl_team_id: 2,
	 tnpl_salary: 2.50,
	 IP: 210.3,
	 ERA: 3.24,
	 ERA_dollar: 1.6,
	 WHIP: 1.09,
	 WHIP_dollar: 1.7,
	 W: 18,
	 W_dollar: 2.2,
	 K: 205,
	 K_dollar: 2.1,
	 S: 0,
	 S_dollar: -0.5,
	 POS: 'P',
	 POS_dollar: 5.51},
	...
];

*/

var TNPL = (function() {
	HittingTable = function(container, data) {
		this.container = $(container);
		this.data = data;
		var self = this;
		create();

		function create() {
			self.displayed_rows = 250;
			self.show_dollars = true;
			self.sortkeys = {'BA_dollar': true,
					 'R_dollar': true,
					 'HR_dollar': true,
					 'RBI_dollar': true,
					 'SB_dollar': true,
					 'POS_dollar': true};
			self.floating_header = null;
			self.floating_headers = null;
			self.table = $('<table />');
			self.thead = $('<thead />');
			self.thead.appendTo(self.table);
			self.headers = {};
			self.header = createHeaderRow(self.headers);
			highlightSortKeys();
			self.header.appendTo(self.thead);
			self.tbody = $('<tbody />').appendTo(self.table);
			sort();
			recreateRows();
			
			
			self.table.appendTo(container);
		}

		function createHeaderRow(sortable_divs) {
			var header = $('<tr />');
			header.appendTo(self.thead);
			$('<th />').appendTo(header).text('Rank');
			$('<th />').appendTo(header).text('Player');
			$('<th />').appendTo(header).text('Team');
			$('<th />').appendTo(header).text('Salary');
			['BA', 'R', 'HR', 'RBI', 'SB', 'POS'].forEach(function(val) {
				var th = $('<th />').appendTo(header);
				var div = $('<div />')
					.addClass('sort-header')
					.text(val)
					.appendTo(th)
					.click(function() {
						var key = val + '_dollar';
						self.sortkeys[key] = !self.sortkeys[key];
						highlightSortKeys();
						sort();
					});
				sortable_divs[val + '_dollar'] = div;
			});
			$('<th />').appendTo(header).text('$ Value');
			return header;
		}

		function highlightSortKeys() {
			for (var i in self.sortkeys) {
				if (self.sortkeys[i]) {
					self.headers[i].addClass('active');
					if (self.floating_header != null) {
						self.floating_headers[i].addClass('active');
					}
				} else {
					self.headers[i].removeClass('active');
					if (self.floating_header != null) {
						self.floating_headers[i].removeClass('active');
					}
				}
			}
		}

		function toggleDollars() {
			self.show_dollars = !self.show_dollars;
			recreateRows();
			destroyFloatingHeader();
			scrollHandler();
		}

		function recreateRows() {
			self.tbody.empty();
			var nrows = Math.min(self.displayed_rows,
					     self.data.length);
			for (var idx = 0; idx < nrows; idx++) {
				var val = self.data[idx];
				var row = $('<tr />');
				if (idx % 2 == 0) {
					row.addClass('odd-row');
				}
				addCellsToRow(row, val, idx);
				row.appendTo(self.tbody);
			}
			if (nrows < self.data.length) {
				var row = $('<tr />');
				var td = $('<td />')
					.attr('colspan', 11)
					.css('text-align', 'center')
					.text('Click for next 50 entries')
					.click(function() {
						self.displayed_rows += 50;
						recreateRows();
					}).appendTo(row);
				row.appendTo(self.tbody);
			}
		}

		function addCellsToRow(row, playerinfo, idx) {
			$('<td />').appendTo(row).text(idx + 1);
			var player_link = $('<a />')
				.attr('href',
				      '/player/' + playerinfo.player_id + '/')
				.text(playerinfo.name);
			$('<td />').append(player_link).appendTo(row);
			if (playerinfo.tnpl_team == null) {
				$('<td />').addClass('highlight').appendTo(row);
				$('<td />').addClass('highlight').appendTo(row);
			} else {
				var team_link = $('<a />')
					.attr('href',
					      '/team/' + playerinfo.tnpl_team_id + '/' + window.location.search)
					.text(playerinfo.tnpl_team);
				$('<td />').append(team_link).appendTo(row);
				$('<td />')
					.text('$' + playerinfo.tnpl_salary.toFixed(2))
					.appendTo(row);
			}
			var ba_td = $('<td />').appendTo(row);
			if (self.show_dollars) {
				var pre = '$';
				if (playerinfo.BA_dollar < 0.0) {
					pre = '-$';
				}
				var dollar_val = Math.abs(playerinfo.BA_dollar);
				ba_td.text(pre + dollar_val.toFixed(2));
			} else {
				ba_td.text('' + playerinfo.BA.toFixed(3) + ' (' +
					   playerinfo.AB + ')');
			}
			['R', 'HR', 'RBI', 'SB', 'POS'].forEach(function(val) {
				var td = $('<td />').appendTo(row);
				if (self.show_dollars) {
					var key = val + '_dollar';
					var pre = '$';
					if (playerinfo[key] < 0.0) {
						pre = '-$';
					}
					var dollar_val = Math.abs(playerinfo[key]);
					td.text(pre + dollar_val.toFixed(2));
				} else {
					td.text(playerinfo[val]);
				}
			});
			var dollar_val = playerinfo.BA_dollar +
					 playerinfo.R_dollar +
					 playerinfo.HR_dollar +
					 playerinfo.RBI_dollar +
					 playerinfo.SB_dollar +
					 playerinfo.POS_dollar;
			var $dollar_val = $('<td />')
				.appendTo(row)
				.text('$' + dollar_val.toFixed(2));
		}

		function sort() {
			self.data.sort(cmp);
			recreateRows();
		}

		function cmp(a, b) {
			var a_key = sortKey(a);
			var b_key = sortKey(b);
			return b_key - a_key;
		}

		function sortKey(row) {
			var sum = 0.0;
			for (var sortkey in self.sortkeys) {
				if (self.sortkeys[sortkey]) {
					sum += row[sortkey];
				}
			}
			return sum;
		}

		function scrollHandler() {
			var offset = self.table.offset();
			scrollTop = $(window).scrollTop();
			if ((scrollTop > offset.top) &&
			    (scrollTop < offset.top + self.table.height())) {
				// Show floating header if it's not already
				createFloatingHeader();
			} else {
				// Hide floating header if it's not already
				destroyFloatingHeader();
			}
		}

		function createFloatingHeader() {
			if (self.floating_header == null) {
				self.floating_headers = {};
				self.floating_header = createHeaderRow(self.floating_headers);
				self.floating_header.before(self.header);
				self.floating_header.css({position: 'fixed', top: 0});
				self.floating_header.children().width(
					function(i,val) {
						return self
							.header
							.children()
							.eq(i)
							.width();
				});
				highlightSortKeys();
			}
		}

		function destroyFloatingHeader() {
			if (self.floating_header != null) {
				self.floating_header.remove();
				self.floating_header = null;
				self.floating_headers = null;
			}
		}

		return {
			toggleDollars: toggleDollars,
			scrollHandler: scrollHandler,
		};
	}

	PitchingTable = function(container, data) {
		this.container = $(container);
		this.data = data;
		var self = this;
		create();

		function create() {
			self.displayed_rows = 250;
			self.show_dollars = true;
			self.sortkeys = {'ERA_dollar': true,
					 'WHIP_dollar': true,
					 'W_dollar': true,
					 'K_dollar': true,
					 'S_dollar': true,
					 'POS_dollar': true};
			self.floating_header = null;
			self.floating_headers = null;
			self.table = $('<table />');
			self.thead = $('<thead />');
			self.thead.appendTo(self.table);
			self.headers = {};
			self.header = createHeaderRow(self.headers);
			highlightSortKeys();
			self.header.appendTo(self.thead);
			self.tbody = $('<tbody />').appendTo(self.table);
			sort();
			recreateRows();
			
			
			self.table.appendTo(container);
		}

		function createHeaderRow(sortable_divs) {
			var header = $('<tr />');
			header.appendTo(self.thead);
			$('<th />').appendTo(header).text('Rank');
			$('<th />').appendTo(header).text('Player');
			$('<th />').appendTo(header).text('Team');
			$('<th />').appendTo(header).text('Salary');
			['ERA', 'WHIP', 'W', 'K', 'S', 'POS'].forEach(function(val) {
				var th = $('<th />').appendTo(header);
				var div = $('<div />')
					.addClass('sort-header')
					.text(val)
					.appendTo(th)
					.click(function() {
						var key = val + '_dollar';
						self.sortkeys[key] = !self.sortkeys[key];
						highlightSortKeys();
						sort();
					});
				sortable_divs[val + '_dollar'] = div;
			});
			$('<th />').appendTo(header).text('$ Value');
			return header;
		}

		function highlightSortKeys() {
			for (var i in self.sortkeys) {
				if (self.sortkeys[i]) {
					self.headers[i].addClass('active');
					if (self.floating_header != null) {
						self.floating_headers[i].addClass('active');
					}
				} else {
					self.headers[i].removeClass('active');
					if (self.floating_header != null) {
						self.floating_headers[i].removeClass('active');
					}
				}
			}
		}

		function toggleDollars() {
			self.show_dollars = !self.show_dollars;
			recreateRows();
			destroyFloatingHeader();
			scrollHandler();
		}

		function recreateRows() {
			self.tbody.empty();
			var nrows = Math.min(self.displayed_rows,
					     self.data.length);
			for (var idx = 0; idx < nrows; idx++) {
				var val = self.data[idx];
				var row = $('<tr />');
				if (idx % 2 == 0) {
					row.addClass('odd-row');
				}
				addCellsToRow(row, val, idx);
				row.appendTo(self.tbody);
			}
			if (nrows < self.data.length) {
				var row = $('<tr />');
				var td = $('<td />')
					.attr('colspan', 11)
					.css('text-align', 'center')
					.text('Click for next 50 entries')
					.click(function() {
						self.displayed_rows += 50;
						recreateRows();
					}).appendTo(row);
				row.appendTo(self.tbody);
			}
		}

		function addCellsToRow(row, playerinfo, idx) {
			$('<td />').appendTo(row).text(idx + 1);
			var player_link = $('<a />')
				.attr('href',
				      '/player/' + playerinfo.player_id + '/')
				.text(playerinfo.name);
			$('<td />').append(player_link).appendTo(row);
			if (playerinfo.tnpl_team == null) {
				$('<td />').addClass('highlight').appendTo(row);
				$('<td />').addClass('highlight').appendTo(row);
			} else {
				var team_link = $('<a />')
					.attr('href',
					      '/team/' + playerinfo.tnpl_team_id + '/')
					.text(playerinfo.tnpl_team);
				$('<td />').append(team_link).appendTo(row);
				$('<td />')
					.text('$' + playerinfo.tnpl_salary.toFixed(2))
					.appendTo(row);
			}
			var era_td = $('<td />').appendTo(row);
			if (self.show_dollars) {
				var pre = '$';
				if (playerinfo.ERA_dollar < 0.0) {
					pre = '-$';
				}
				var dollar_val = Math.abs(playerinfo.ERA_dollar);
				era_td.text(pre + dollar_val.toFixed(2));
			} else {
				era_td.text('' + playerinfo.ERA.toFixed(3) + ' (' +
					   playerinfo.IP.toFixed(1) + ')');
			}
			var whip_td = $('<td />').appendTo(row);
			if (self.show_dollars) {
				var pre = '$';
				if (playerinfo.WHIP_dollar < 0.0) {
					pre = '-$';
				}
				var dollar_val = Math.abs(playerinfo.WHIP_dollar);
				whip_td.text(pre + dollar_val.toFixed(2));
			} else {
				whip_td.text('' + playerinfo.WHIP.toFixed(3) + ' (' +
					   playerinfo.IP.toFixed(1) + ')');
			}
			['W', 'K', 'S', 'POS'].forEach(function(val) {
				var td = $('<td />').appendTo(row);
				if (self.show_dollars) {
					var key = val + '_dollar';
					var pre = '$';
					if (playerinfo[key] < 0.0) {
						pre = '-$';
					}
					var dollar_val = Math.abs(playerinfo[key]);
					td.text(pre + dollar_val.toFixed(2));
				} else {
					td.text(playerinfo[val]);
				}
			});
			var dollar_val = playerinfo.ERA_dollar +
					 playerinfo.WHIP_dollar +
					 playerinfo.W_dollar +
					 playerinfo.K_dollar +
					 playerinfo.S_dollar +
					 playerinfo.POS_dollar;
			var $dollar_val = $('<td />')
				.appendTo(row)
				.text('$' + dollar_val.toFixed(2));
		}

		function sort() {
			self.data.sort(cmp);
			recreateRows();
		}

		function cmp(a, b) {
			var a_key = sortKey(a);
			var b_key = sortKey(b);
			return b_key - a_key;
		}

		function sortKey(row) {
			var sum = 0.0;
			for (var sortkey in self.sortkeys) {
				if (self.sortkeys[sortkey]) {
					sum += row[sortkey];
				}
			}
			return sum;
		}

		function scrollHandler() {
			var offset = self.table.offset();
			scrollTop = $(window).scrollTop();
			if ((scrollTop > offset.top) &&
			    (scrollTop < offset.top + self.table.height())) {
				// Show floating header if it's not already
				createFloatingHeader();
			} else {
				// Hide floating header if it's not already
				destroyFloatingHeader();
			}
		}

		function createFloatingHeader() {
			if (self.floating_header == null) {
				self.floating_headers = {};
				self.floating_header = createHeaderRow(self.floating_headers);
				self.floating_header.before(self.header);
				self.floating_header.css({position: 'fixed', top: 0});
				self.floating_header.children().width(
					function(i,val) {
						return self
							.header
							.children()
							.eq(i)
							.width();
				});
				highlightSortKeys();
			}
		}

		function destroyFloatingHeader() {
			if (self.floating_header != null) {
				self.floating_header.remove();
				self.floating_header = null;
				self.floating_headers = null;
			}
		}

		return {
			toggleDollars: toggleDollars,
			scrollHandler: scrollHandler,
		};
	}

	return {
		HittingTable: HittingTable,
		PitchingTable: PitchingTable,
	};
})();
