/*
data = {
	headers: [
		{ title: 'Name',
		  cumulative: false},
		{ title: 'HR',
		  cumulative: true},
	],
	rows: [ 
		[ {value: 'John Doe'
		   link: '/player/1234'},
		   25
		],
		[ {value: 'Joe Foo',
		   link: '/player/12345'},
		  30
		]
	]
}
*/

var TNPL = (function() {
	StatsTable = function(container, data) {
		this.container = $(container);
		this.data = data;

		var self = this;

		function create() {
			self.sortkeys = {};
			self.table = $('<table />');
			self.table.appendTo(self.container);
			self.thead = $('<thead />');
			self.thead.appendTo(self.table);
			var tr = $('<tr />');
			tr.appendTo(self.thead);
			var header = $('<th />');
			header.text('Rank');
			header.appendTo(tr);
			self.data.headers.forEach(function(val, idx) {
				var header = $('<th />');
				header.appendTo(tr);
				if (val.cumulative) {
					var div = $('<div />');
					div.text(val.title);
					div.addClass('active sort-header');
					div.appendTo(header);
					self.sortkeys[idx] = true;
					div.click(function() {
						if (idx in self.sortkeys) {
							delete self.sortkeys[idx];
							div.removeClass('active');
						} else {
							self.sortkeys[idx] = true;
							div.addClass('active');
						}
						sort();
					});
				} else {
					header.text(val.title);
				}
			});
			header = $('<th />');
			header.appendTo(tr);
			header.text('Sum');
			self.tbody = $('<tbody />');
			self.tbody.appendTo(self.table);
			sort();
		}

		create();

		function sort_key(row) {
			var sum = 0;
			for (var idx in self.sortkeys) {
				if (typeof row[idx] == "object") {
					sum += row[idx].value;
				} else {
					sum += row[idx];
				}
			}
			return sum;
		}

		function cmp(a, b) {
			var a_key = sort_key(a);
			var b_key = sort_key(b);
			return b_key - a_key;
		}

		function sort() {
			self.data.rows.sort(cmp);
			teardown();
			self.data.rows.forEach(function(row, row_idx) {
				var max_precision = 0;
				var tr = $('<tr />');
				tr.appendTo(self.tbody);
				if (row_idx % 2 == 1) {
					tr.addClass('odd-row');
				}
				var td = $('<td />');
				td.text(row_idx + 1);
				td.appendTo(tr);
				row.forEach(function(col, col_idx) {
					var td = $('<td />');
					if (col != null) {
						var tofixed = false;
						if ('tofixed' in self.data.headers[col_idx]) {
							tofixed = self.data.headers[col_idx].tofixed;
							if (max_precision < tofixed) {
								max_precision = tofixed;
							}
						}
						if (typeof col == "object") {
							if ('link' in col) {
								var anchor = $('<a />');
								anchor.attr('href', col.link);
								if (tofixed === false) {
									anchor.text(col.value);
								} else {
									anchor.text(col.value.toFixed(tofixed));
								}
								anchor.appendTo(td);
							} else if (col.value != null) {
								if (tofixed == false) {
									td.text(col.value);
								} else {
									td.text(col.value.toFixed(tofixed));
								}
							}
							if ('highlight' in col && col.highlight) {
								td.addClass('highlight');
							}
						} else {
							if (tofixed === false) {
								td.text(col);
							} else {
								td.text(col.toFixed(tofixed));
							}
						}
					}
					td.appendTo(tr);
				});
				var td = $('<td />');
				var sum = sort_key(row);
				td.text(sum.toFixed(max_precision));
				td.appendTo(tr);
			});
		}

		function teardown() {
			self.tbody.empty();
		}

		return this;
	}

	return {
		StatsTable: StatsTable,
	};
})();
