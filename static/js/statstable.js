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
			self.displayed_rows = 500;
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
			var tbody = self.tbody[0];
			var rowSel = d3.select(tbody).selectAll('tr')
				.data(self.data.slice(0, self.displayed_rows));
			rowSel.enter()
				.append('tr');
			rowSel.exit()
				.remove();
			rowSel
				.classed('odd-row', function(d,i) { return i % 2 == 1; })
				.call(addCellsToRow);
		}

		function addCellsToRow(selection) {
			selection.each(function(d,i) {
				var row = d3.select(this);
				var tdSel = row.selectAll('td')
					.data(function(d) {
						var cols = [];
						var total_val = d.BA_dollar + d.R_dollar + d.HR_dollar + d.RBI_dollar + d.SB_dollar + d.POS_dollar;
						cols.push({type: 'rank', value: i+1});
						cols.push({type: 'player', name: d.name, id: d.player_id});
						cols.push({type: 'team', name: d.tnpl_team, id: d.tnpl_team_id});
						cols.push({type: 'salary', value: d.tnpl_salary});
						cols.push({type: 'BA', dollar_value: d.BA_dollar, value: d.BA, ab: d.AB});
						cols.push({type: 'R', dollar_value: d.R_dollar, value: d.R});
						cols.push({type: 'HR', dollar_value: d.HR_dollar, value: d.HR});
						cols.push({type: 'RBI', dollar_value: d.RBI_dollar, value: d.RBI});
						cols.push({type: 'SB', dollar_value: d.SB_dollar, value: d.SB});
						cols.push({type: 'POS', dollar_value: d.POS_dollar, value: d.POS});
						cols.push({type: 'value', value: total_val});
						return cols;
					});
				tdSel.enter()
					.append('td');
				tdSel.exit()
					.remove();
				tdSel.each(function(d) {
					var td = d3.select(this);
					if (d.type === 'rank') {
						td.text(d.value);
					} else if (d.type === 'player') {
						var aSel = td.selectAll('a').data([d]);
						aSel.enter().append('a');
						aSel.exit().remove();
						aSel
							.attr('href', '/player/' + d.id + '/')
							.text(d.name);
					} else if (d.type === 'team') {
						var anchorData = [];
						if (d.id === null || d.name === null) {
							td.classed('highlight', true);
						} else {
							anchorData = [d];
							td.classed('highlight', false);
						}
						var aSel = td.selectAll('a').data(anchorData);
						aSel.enter().append('a');
						aSel.exit().remove();
						aSel
							.attr('href', function(d) { return '/team/' + d.id + '/' + window.location.search; })
							.text(function(d) { return d.name; });
					} else if (d.type === 'salary') {
						if (d.value === null) {
							td
								.classed('highlight', true)
								.text('');
						} else {
							td
								.classed('highlight', false)
								.text('$' + d.value.toFixed(2));
						}
					} else if (d.type === 'BA') {
						if (self.show_dollars) {
							var pre = '$';
							if (d.dollar_value < 0.0) {
								pre = '-$';
							}
							var dollar_val = Math.abs(d.dollar_value);
							td.text(pre + dollar_val.toFixed(2));
						} else {
							td.text('' + d.value.toFixed(3) + ' (' + d.ab + ')');
						}
					} else if (['R', 'HR', 'RBI', 'SB', 'POS'].indexOf(d.type) >= 0) {
						if (self.show_dollars) {
							var pre = '$';
							if (d.dollar_value < 0.0) {
								pre = '-$';
							}
							var dollar_val = Math.abs(d.dollar_value);
							td.text(pre + dollar_val.toFixed(2));
						} else {
							td.text(d.value);
						}
						
					} else if (d.type === 'value') {
						var pre = '$';
						if (d.value < 0.0) {
							pre = '-$';
						}
						var dollar_val = Math.abs(d.value);
						td.text(pre + dollar_val.toFixed(2));
					}
				});	
			});
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
			self.displayed_rows = 500;
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
			var tbody = self.tbody[0];
			var rowSel = d3.select(tbody).selectAll('tr')
				.data(self.data.slice(0, self.displayed_rows));
			rowSel.enter()
				.append('tr');
			rowSel.exit()
				.remove();
			rowSel
				.classed('odd-row', function(d,i) { return i % 2 == 1; })
				.call(addCellsToRow);
		}

		function addCellsToRow(selection) {
			selection.each(function(d,i) {
				var row = d3.select(this);
				var tdSel = row.selectAll('td')
					.data(function(d) {
						var cols = [];
						var total_val = d.ERA_dollar + d.WHIP_dollar + d.W_dollar + d.K_dollar + d.S_dollar + d.POS_dollar;
						cols.push({type: 'rank', value: i+1});
						cols.push({type: 'player', name: d.name, id: d.player_id});
						cols.push({type: 'team', name: d.tnpl_team, id: d.tnpl_team_id});
						cols.push({type: 'salary', value: d.tnpl_salary});
						cols.push({type: 'ERA', dollar_value: d.ERA_dollar, value: d.ERA, ip: d.IP});
						cols.push({type: 'WHIP', dollar_value: d.WHIP_dollar, value: d.WHIP, ip: d.IP});
						cols.push({type: 'W', dollar_value: d.W_dollar, value: d.W});
						cols.push({type: 'K', dollar_value: d.K_dollar, value: d.K});
						cols.push({type: 'S', dollar_value: d.S_dollar, value: d.S});
						cols.push({type: 'POS', dollar_value: d.POS_dollar, value: d.POS});
						cols.push({type: 'value', value: total_val});
						return cols;
					});
				tdSel.enter()
					.append('td');
				tdSel.exit()
					.remove();
				tdSel.each(function(d) {
					var td = d3.select(this);
					if (d.type === 'rank') {
						td.text(d.value);
					} else if (d.type === 'player') {
						var aSel = td.selectAll('a').data([d]);
						aSel.enter().append('a');
						aSel.exit().remove();
						aSel
							.attr('href', '/player/' + d.id + '/')
							.text(d.name);
					} else if (d.type === 'team') {
						var anchorData = [];
						if (d.id === null || d.name === null) {
							td.classed('highlight', true);
						} else {
							anchorData = [d];
							td.classed('highlight', false);
						}
						var aSel = td.selectAll('a').data(anchorData);
						aSel.enter().append('a');
						aSel.exit().remove();
						aSel
							.attr('href', function(d) { return '/team/' + d.id + '/' + window.location.search; })
							.text(function(d) { return d.name; });
					} else if (d.type === 'salary') {
						if (d.value === null) {
							td
								.classed('highlight', true)
								.text('');
						} else {
							td
								.classed('highlight', false)
								.text('$' + d.value.toFixed(2));
						}
					} else if (d.type === 'ERA' || d.type === 'WHIP') {
						if (self.show_dollars) {
							var pre = '$';
							if (d.dollar_value < 0.0) {
								pre = '-$';
							}
							var dollar_val = Math.abs(d.dollar_value);
							td.text(pre + dollar_val.toFixed(2));
						} else {
							td.text('' + d.value.toFixed(3) + ' (' + d.ip.toFixed(1) + ')');
						}
					} else if (['W', 'K', 'S', 'POS'].indexOf(d.type) >= 0) {
						if (self.show_dollars) {
							var pre = '$';
							if (d.dollar_value < 0.0) {
								pre = '-$';
							}
							var dollar_val = Math.abs(d.dollar_value);
							td.text(pre + dollar_val.toFixed(2));
						} else {
							td.text(d.value);
						}
						
					} else if (d.type === 'value') {
						var pre = '$';
						if (d.value < 0.0) {
							pre = '-$';
						}
						var dollar_val = Math.abs(d.value);
						td.text(pre + dollar_val.toFixed(2));
					}
				});	
			});
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
