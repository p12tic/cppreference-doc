/*
    Copyright (C) 2013-2014  Povilas Kanapickas <povilas@radix.lt>

    This file is part of cppreference.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
*/

$(function() {

    function array_equal(a, b) {
        var i = a.length;
        if (i != b.length) {
            return false;
        }
        while (i--) {
            if (a[i] !== b[i]) {
                return false;
            }
        }
        return true;
    };

    function array_sort_unique(a) {
        a = a.sort(function(x, y) { return x - y; });
        var c = a[0];
        var res = [c];
        for (var i = 1; i < a.length; i++) {
            if (a[i] !== c) {
                res.push(a[i]);
                c = a[i];
            }
        }
        return res;
    }

    // supports only arrays of bool
    function array_and(a, b) {
        var res = [];
        var length = a.length < b.length ? a.length : b.length;
        for (var i = 0; i < length; i++) {
            res.push(a[i] && b[i]);
        }
        return res;
    }
    // supports only arrays of bool
    function array_or(a, b) {
        var res = [];
        var length = a.length < b.length ? a.length : b.length;
        for (var i = 0; i < length; i++) {
            res.push(a[i] || b[i]);
        }
        return res;
    }

    if (mw.config.get('wgAction') != 'view') {
        return;
    }
    if (mw.config.get('wgNamespaceNumber') != 0) {
        return;
    }

    /// Are we dealing with C or C++
    var is_cxx = (mw.config.get('wgTitle').indexOf('c/') != 0);

    /// Standard revision identification 'enums'

    var Rev_c = { DIFF: 0, FIRST: 1, C89: 1, C99: 2, C11: 3, LAST: 4 };
    var Rev_cxx = { DIFF: 0, FIRST: 1, CXX98: 1, CXX11: 2, CXX14: 3, LAST: 4 };

    var Rev;

    if (is_cxx) {
        Rev = Rev_cxx;
    } else {
        Rev = Rev_c;
    }

    /// Standard revision description strings
    var desc_c = [
        { rev: Rev.DIFF, title: 'Diff' },
        { rev: Rev.C89, title: 'C89' },
        { rev: Rev.C99, title: 'C99' },
        { rev: Rev.C11, title: 'C11' },
    ];

    var desc_cxx = [
        { rev: Rev.DIFF, title: 'Diff' },
        { rev: Rev.CXX98, title: 'C++98/03' },
        { rev: Rev.CXX11, title: 'C++11' },
        { rev: Rev.CXX14, title: 'C++14' },
    ];

    var desc;

    if (is_cxx) {   // select either C or C++ version
        desc = desc_cxx;
    } else {
        desc = desc_c;
    }

    /// Several helper arrays and functions to identify on which revisions
    /// certain mark is shown.

    var is_shown = [];

    function should_be_shown(rev, mark) {
        if (rev == Rev.DIFF) {
            return true;
        }
        if (mark.since) {
            return (rev >= mark.rev);
        } else {
            return (rev < mark.rev);
        }
    }

    /** Returns mark for element. Use when at most single mark can be present */
    function get_mark_cxx(el) {
        if (el.hasClass('t-since-cxx11')) {
            return { since: true, rev: Rev.CXX11 };
        }
        if (el.hasClass('t-since-cxx14')) {
            return { since: true, rev: Rev.CXX14 };
        }
        if (el.hasClass('t-until-cxx11')) {
            return { since: false, rev: Rev.CXX11 };
        }
        if (el.hasClass('t-until-cxx14')) {
            return { since: false, rev: Rev.CXX14 };
        }
        return { since: true, rev: Rev.CXX98 };
    }

    function get_mark_c(el) {
        if (el.hasClass('t-since-c99')) {
            return { since: true, rev: Rev.C99 };
        }
        if (el.hasClass('t-since-c11')) {
            return { since: true, rev: Rev.C11 };
        }
        if (el.hasClass('t-until-c99')) {
            return { since: false, rev: Rev.C99 };
        }
        if (el.hasClass('t-until-c11')) {
            return { since: false, rev: Rev.C11 };
        }
        return { since: true, rev: Rev.C89 };
    }

    /** Returns an array of revisions (DIFF not included) an element should be
        shown on.
    */
    function is_shown_on_rev_cxx(el) {
        // DIFF: 0, CXX98: 1, CXX11: 2, CXX14: 3
        // DIFF is always false
        if (el.hasClass('t-since-cxx14')) {
            return [false, false, false, true];
        }
        if (el.hasClass('t-since-cxx11')) {
            if (el.hasClass('t-until-cxx14')) {
                return [false, false, true, false];
            }
            return [false, false, true, true];
        }
        if (el.hasClass('t-until-cxx11')) {
            return [false, true, false, false];
        }
        if (el.hasClass('t-until-cxx14')) {
            return [false, true, true, false];
        }
        return [false, true, true, true];
    }

    function is_shown_on_rev_c(el) {
        // DIFF: 0, C89: 1, C99: 2, C11: 3
        // DIFF is always false
        if (el.hasClass('t-since-c11')) {
            return [false, false, false, true];
        }
        if (el.hasClass('t-since-c99')) {
            if (el.hasClass('t-until-c11')) {
                return [false, false, true, false];
            }
            return [false, false, true, true];
        }
        if (el.hasClass('t-until-c99')) {
            return [false, true, false, false];
        }
        if (el.hasClass('t-until-c11')) {
            return [false, true, true, false];
        }
        return [false, true, true, true];
    }

    function is_shown_fill_cxx(val) {
        // DIFF: 0, CXX98: 1, CXX11: 2, CXX14: 3
        return [val, val, val, val];
    }
    function is_shown_fill_c(el) {
        // DIFF: 0, C89: 1, C99: 2, C11: 3
        return [val, val, val, val];
    }

    var get_mark, is_shown_on_rev, is_shown_fill;

    if (is_cxx) {   // select either C or C++ version
        get_mark = get_mark_cxx;
        is_shown_on_rev = is_shown_on_rev_cxx;
        is_shown_fill = is_shown_fill_cxx;
    } else {
        get_mark = get_mark_c;
        is_shown_on_rev = is_shown_on_rev_c;
        is_shown_fill = is_shown_fill_c;
    }

    function get_shown_revs(el) {
        var is_shown = is_shown_on_rev(el);
        var res = [];
        for (var i = Rev.FIRST; i != Rev.LAST; ++i) {
            if (is_shown[i]) {
                res.push(i);
            }
        }
        return res;
    }

    /** Converts array of bool as returned by @c is_shown_on_rev or
        @c is_shown_fill to an array of revisions as accepted by ObjectTracker's
        add_* methods
    */
    function is_shown2revs(revs) {
        var res = [];
        for (var rev = Rev.DIFF; rev != Rev.LAST; ++rev) {
            if (revs[rev]) {
                res.push(rev);
            }
        }
        return res;
    }

    /** This class keeps track of objects that need to be shown or hidden for
        specific standard revision.
    */
    function ObjectTracker() {

        this.all_objects = [];
        // jQuery screws up restoring correct display property
        this.all_display = [];

        this.diff_ids = [];
        this.curr_rev = Rev.DIFF;

        // Maps revisions to object indexes within this.all_objects.
        this.rev2id_map = [];
        for (var i = 0; i < Rev.LAST; ++i) {
            this.rev2id_map[i] = [];
        }

        /** Adds a jQuery object @a obj from the original document DOM. @a revs
            define for which standard revisions to display the object. @a
            display defines the CSS display property to use when the object is
            shown.

            Returns the id of the new object.
        */
        this.add_diff_object = function(obj, revs, display) {
            var id = this.add_object(obj, revs, display);
            this.diff_ids.push(id);
            return id;
        };

        /** Adds a jQuery object @a obj that is newly created, i.e. modified
            version of an object that has been/will be passed to
            add_diff_object. @a revs define for which standard revisions to
            display the object. @a display defines the CSS display property to
            use when the object is shown.

            Returns the id of the new object.
        */
        this.add_object = function(obj, revs, display) {
            var id = this.all_objects.length;
            this.all_objects[id] = obj;
            this.all_display[id] = display;

            for (var i = 0; i < revs.length; ++i) {
                this.rev2id_map[revs[i]].push(id);
            }
            return id;
        };

        /** Changes the visibility of objects */
        this.to_rev = function(rev) {
            if (rev == this.curr_rev) {
                return;
            }
            var visible_before = this.rev2id_map[this.curr_rev];
            var visible_after = this.rev2id_map[rev];

            for (var i = 0; i < visible_before.length; ++i) {
                var curr = visible_before[i];
                if ($.inArray(curr, visible_after) == -1) {
                    this.all_objects[curr].css('display', 'none');
                }
            }
            for (var i = 0; i < visible_after.length; ++i) {
                var curr = visible_after[i];
                if ($.inArray(curr, visible_before) == -1) {
                    this.all_objects[curr].css('display', this.all_display[curr]);
                }
            }
            this.curr_rev = rev;
        };
    };

    function StandardRevisionPlugin() {

        this.el = {};
        this.el.root = $('#mw-content-text').first();
        this.curr_rev = Rev.DIFF;

        this.tracker = new ObjectTracker();
        this.is_prepared = false;

        /** Prepares the navbar for versioning using object tracker. As the
            navbar contains many items, committing each of them to the object
            tracker, we make as many copies of the original navbar as there are
            revisions and customize each copy in-place.
        */
        this.prepare_navbar = function() {
            var nv = this.el.root.children('.t-navbar'); // main navbar
            if (nv.length == 0) {
                return; // no navbar
            }

            this.tracker.add_diff_object(nv, [Rev.DIFF], 'block');

            var self = this;

            for (var rev = Rev.FIRST; rev < Rev.LAST; ++rev) {
                // Create new navbar and insert it to the tracker
                var rev_nv = nv.clone().hide().insertAfter(nv);
                this.tracker.add_object(rev_nv, [rev], 'block');

                // Get interesting elements
                var nv_tables = rev_nv.find('.t-nv-begin');
                var nv_tables_tb = nv_tables.children('tbody');

                var el_h1 = nv_tables_tb.children('.t-nv-h1');
                var el_h2 = nv_tables_tb.children('.t-nv-h2');
                var el_col_tables = nv_tables_tb.children('.t-nv-col-table');
                var el_nv = nv_tables_tb.children('.t-nv');

                // Remove entries from the link tables that should not be visible
                // for the revision in question
                el_nv.each(function(){

                    // Get the link table
                    var link_tds = $(this).find('.t-nv-ln-table div');

                    if (link_tds.length == 0) {
                        // bare nv template used. Check if we don't have a mark
                        // template by chance
                        var marks = $(this).find('.t-mark-rev');
                        if (marks.length > 0) {
                            var mark = get_mark(marks.first());
                            if (!should_be_shown(rev, mark)) {
                                $(this).remove();
                            } else {
                                marks.remove(); // do not show marks in any case
                            }
                        }
                        return;
                    }

                    if (link_tds.length == 1) {
                        // The earliest standard (always visible)
                        return;
                    }
                    var titles = link_tds.first().children().children().first().children();
                    var marks = link_tds.last().children().first().children();

                    // Delete the lines
                    if (self.delete_lines(titles, marks, rev)) {
                        $(this).remove();
                    }
                });

                // Remove all empty column tables
                el_col_tables.each(function() {
                    if ($(this).find('.t-nv').length == 0) {
                        $(this).remove();
                    }
                });

                // Look for any headings that do not have items after them
                el_h2.each(function() {
                    if ($(this).next().length == 0 ||
                        $(this).next().is('.t-nv-h2, .t-nv-h1')
                    ) {
                        $(this).remove();
                    }
                });

                el_h1.each(function() {
                    if ($(this).next().length == 0 ||
                        $(this).next().is('.t-nv-h1')
                    ) {
                        $(this).remove();
                    }
                });

                // TODO: perhaps it's worth to reflow the remaining columns
            }
        };

        /** rev list template can be prepared separately from everything else.
            Additionally, we don't need to copy any parts of the object tree:
            the elements within table rev list just need to be hidder or shown
            depending on the revision
        */
        this.prepare_revs = function() {
            this.rev_tables = $('.t-rev-begin');
            var rev_elems = this.rev_tables.children('tbody').children('.t-rev');
            var self = this;
            rev_elems.each(function() {
                var shown_revs = get_shown_revs($(this));
                shown_revs.push(Rev.DIFF);

                self.tracker.add_object($(this), shown_revs, 'block');
            });
        };

        /** Prepares items in dsc lists */
        this.prepare_dscs = function() {
            this.dsc_tables = $('.t-dsc-begin');
            var dsc_elems = this.dsc_tables.children('tbody').children('.t-dsc');

            // FIXME: handle type tables
            var self = this;
            dsc_elems.each(function(){
                var member = $(this).children().children('.t-dsc-member-div');
                if (member.length == 0) {
                    return;
                }
                var lines = member.find('.t-lines');
                if (lines.length != 2) {
                    return;
                }
                var marks = lines.last();

                var rev_map = self.get_revision_map(marks.children());
                self.tracker.add_diff_object($(this), rev_map[Rev.DIFF], 'table-row');

                var sep_rev = rev_map[Rev.DIFF]; // separator visibility
                for (var rev = Rev.FIRST; rev < Rev.LAST; ++rev) {
                    if (rev_map[rev].length == 0) {
                        continue;
                    }
                    sep_rev = sep_rev.concat(rev_map[rev]);

                    var copy = $(this).clone().hide();
                    self.tracker.add_object(copy, rev_map[rev], 'table-row');

                    var member = copy.children().children('.t-dsc-member-div');
                    var lines = member.find('.t-lines');
                    var titles = lines.first().children();
                    var marks = lines.last().children();

                    self.delete_lines(titles, marks, rev);
                    copy.insertAfter($(this));
                }

                // hide the separator when we don't show the dsc item
                var sep = $(this).prev('.t-dsc-sep');
                if (sep.length > 0) {
                    self.tracker.add_diff_object(sep, sep_rev, 'table-row');
                }
            });
        };

        /** Prepares items in dcl list identified by @a dcl_table. Returns
            "numbering map", which defines how the list items are renumbered
            (or deleted) for each revision. The numbering map is a an
            two-dimensional array - the first index identifies the revision,
            the second -- original number. The value obtained this way
            identifies whether the entry should be hidden and if not, what
            version number should be displayed on the specific revision. Hidden
            entry is identified by -1.

            array[revision][orig_num] -> target_num or -1
        */
        this.prepare_dcls = function(dcl_table) {

            var tracker = this.tracker;

            // get abstract description of the contents
            defs = [];

            /*
                <Simple dcl> :== {
                    type: 'i',
                    obj: <jQuery object>

                    // The format is the same as returned by is_shown_on_ref
                    // revs[Rev.DIFF] being true identifies that no versioning
                    // information has been provided.
                    revs: 'shown_revs',

                    // -1 if not defined
                    num: 'orig_num'
                }

                <Rev-list dcl> :== {
                    type: 'r',
                    obj: <jQuery object>,
                    revs: 'shown_revs',  // see notes for <Simple dcl>
                    num: 'orig_num',     // -1 if not defined
                    aux: <jQuery object>, // potentially empty

                    // The list of indexes of entries in defs array identifying
                    // children dcls
                    children: [ <child id>, ... ]
                }

                defs: [ <either Simple dcl or rev-list dcl>, ... ]

                If rev-list dcl has 'revs' defined, then those override revs for
                all children dcls.

                If rev-list dcl has 'num' defined, then 'num' for all children
                dcls is -1.
            */
            var num_regex = /\s*\((\d+)\)\s*/;
            function process_tr(el, is_num_overridden, is_rev_overridden,
                                overridden_revs) {
                var new_def = {
                    type: 's',
                    obj: el,
                    num: -1,
                    revs: is_shown_fill(true)
                };

                // get version num
                if (!is_num_overridden) {
                    var num_text = el.children('td').eq(1).text();
                    var match = num_text.match(num_regex);
                    if (match !== null) {
                        new_def.num = parseInt(match[1]);
                    }
                }

                // get revision info
                if (!is_rev_overridden) {
                    var notes_td = el.children('td').eq(2);
                    if (notes_td.find('.t-mark-rev').length > 0) {
                        new_def.revs = is_shown_on_rev(el);
                    }
                } else {
                    new_def.revs = overridden_revs;
                }

                return defs.push(new_def) - 1;
            };

            function process_rev_tbody(el) {
                var new_def = {
                    type: 'r',
                    obj: el,
                    num: -1,
                    revs: is_shown_fill(true),
                    children: []
                };

                // potentially empty
                var aux_tr = el.children('.t-dcl-rev-aux').first();
                new_def.aux = aux_tr;

                // get version num
                var has_num = false;
                if (el.hasClass('t-dcl-rev-num')) {
                    var num_text = aux_tr.children('td').eq(1).text();
                    var match = num_text.match(num_regex);
                    if (match !== null) {
                        new_def.num = parseInt(match[1]);
                        has_num = true;
                    }
                }

                // get revision info
                var has_revs = false;
                if (el.hasClass('t-dcl-rev-notes')) {
                    var mark_revs = aux_tr.children('td').eq(2).find('.t-mark-rev');
                    if (mark_revs.length > 0) {
                        new_def.revs = is_shown_on_rev(el);
                        has_revs = true;
                    }
                }

                // process the member dcls
                el.children('.t-dcl').each(function() {
                    var new_id = process_tr($(this), has_num, has_revs,
                                            new_def.revs.slice());
                    new_def.children.push(new_id);
                });

                defs.push(new_def);
            };

            $(dcl_table).children('tbody').each(function() {
                if ($(this).hasClass('t-dcl-rev')) {
                    process_rev_tbody($(this));
                } else {
                    $(this).children('.t-dcl').each(function() {
                        process_tr($(this), false, false, []);
                    });
                }
            });

            // Get the mapping between revisions and function version numbers

            /* Get the mapping between revisions and function version numbers.
               The function returns an array:

               array[revision][source version number] -> version number to display
            */
            function get_num_map() {
                var num_map = [];

                // We need the maximum visible num to initialize the result array
                // properly
                var max_num = -1;
                for (var i = 0; i < defs.length; ++i) {
                    if (defs[i].num > max_num) {
                        max_num = defs[i].num;
                    }
                }

                if (max_num > -1) {

                    for (var rev = Rev.FIRST; rev != Rev.LAST; ++rev) {

                        var visible_nums = [];

                        for (var i = 0; i < defs.length; ++i) {
                            if (defs[i].revs[rev] == true &&
                                defs[i].num != -1) {
                                visible_nums.push(defs[i].num);
                            }
                        }

                        visible_nums = array_sort_unique(visible_nums);

                        var curr_map = [-1];
                        for (var num = 1; num <= max_num; ++num) {
                            curr_map[num] = -1;
                        }

                        var curr_num = 1;
                        for (var i = 0; i < visible_nums.length; ++i) {
                            curr_map[visible_nums[i]] = curr_num;
                            curr_num++;
                        }
                        num_map[rev] = curr_map;
                    }
                }
                return num_map;
            };

            var num_map = get_num_map();
            // Analyze the abstract description again and modify the DOM
            function clear_rev_marks(tr) {
                marks = tr.children('td').eq(2).find('.t-mark-rev');
                marks.each(function() {
                    // remove only one <br>
                    $(this).prev('br').add($(this).next('br')).first().remove();
                    $(this).remove();
                });
            };

            function set_number(tr, num) {
                tr.children('td').eq(1).text('('+num.toString()+')');
            };

            function get_tr_nums(num) {
                var nums = [];
                for (var rev = Rev.FIRST; rev != Rev.LAST; ++rev) {
                    nums[rev] = num_map[rev][num];
                }
                return nums;
            };

            /// Checks whether any children of a rev-list identified by @a def
            /// are shown in revision @a rev
            function is_children_shown_on_rev(def) {
                var res = is_shown_fill(false);

                for (var i = 0; i != def.children.length; ++i) {
                    res = array_or(res, defs[def.children[i]].revs);
                }
                res[Rev.DIFF] = false;
                return res;
            };

            /** Returns infomation about the required copies of the base
                element.
            */
            function get_copy_info(revs, nums) {
                var res = [];

                var base_rev;   // Don't create a new element if it would
                var new_num;    // be identical to previous one
                var new_revs;
                var is_first = true;

                for (var rev = Rev.FIRST; rev != Rev.LAST; ++rev) {
                    if (!revs[rev]) {
                        continue;
                    }
                    if (!is_first && new_num == nums[rev]) {
                        // Identical element already exists
                        new_revs.push(rev);
                        continue;
                    }

                    if (!is_first) {
                        res.push({ base_rev: base_rev, revs: new_revs,
                                   num: new_num });
                    }

                    base_rev = rev;
                    new_num = nums[rev];
                    new_revs = [rev];
                    is_first = false;
                }
                if (!is_first) {
                    res.push({ base_rev: base_rev, revs: new_revs,
                               num: new_num });
                }
                return res;
            };

            function finalize_tr(def) {
                var sep_revs;

                if (def.num == -1) {
                    var tr_revs = is_shown2revs(def.revs);
                    sep_revs = tr_revs;
                    if (def.revs[Rev.DIFF] == true) {
                        // no num and no rev-marks -- shown always
                        tracker.add_diff_object(def.obj, tr_revs, 'table-row');
                    } else {
                        // no num -- two versions: one with rev-marks and
                        // one without
                        var new_el = def.obj.clone().hide().insertAfter(def.obj);
                        clear_rev_marks(new_el);
                        tracker.add_diff_object(def.obj, [Rev.DIFF], 'table-row');
                        tracker.add_object(new_el, tr_revs, 'table-row');
                        sep_revs.push(Rev.DIFF);
                    }
                } else {
                    // need to handle numbering
                    var nums = get_tr_nums(def.num);

                    tracker.add_diff_object(def.obj, [Rev.DIFF], 'table-row');

                    var copy_info = get_copy_info(def.revs, nums);

                    sep_revs = [Rev.DIFF];
                    for (var i = 0; i < copy_info.length; i++) {
                        var new_el = def.obj.clone().hide().insertAfter(def.obj);
                        clear_rev_marks(new_el);
                        set_number(new_el, copy_info[i].num);
                        tracker.add_object(new_el, copy_info[i].revs, 'table-row');
                        sep_revs = sep_revs.concat(copy_info[i].revs);
                    }
                }

                // hide the separator if needed
                var sep_obj = def.obj.prev('.t-dcl-sep');
                if (sep_obj.length > 0) {
                    tracker.add_diff_object(sep_obj, sep_revs, 'table-row');
                }
            };

            // Roughly the same as finalize_tr, but while all modifications are
            // applied to the t-dcl-rev-aux element, we hide entire tbody
            // section when it has no contents or defs[i].revs[rev] == false
            function finalize_rev_tbody(def) {
                // The rev-list tbody does not ever change - we only need to
                // hide it sometimes
                var tbody_revs = array_and(def.revs, is_children_shown_on_rev(def));
                tbody_revs[Rev.DIFF] = true;
                tracker.add_diff_object(def.obj, is_shown2revs(tbody_revs), 'table-row');

                if (def.num == -1) {
                    if (def.revs[Rev.DIFF] == true) {
                        // No num and no rev-marks -- no further modifications
                        // needed.

                    } else {
                        // No num -- two versions: one with rev-marks and
                        // one without
                        var new_el = def.aux.clone().hide().insertAfter(def.aux);
                        clear_rev_marks(new_el);
                        tracker.add_diff_object(def.aux, [Rev.DIFF], 'table-row');
                        var revs = tbody_revs.slice();
                        revs[Rev.DIFF] = false;

                        tracker.add_object(new_el, is_shown2revs(revs), 'table-row');
                    }
                } else {
                    // need to handle numbering
                    var nums = get_tr_nums(def.num);

                    tracker.add_diff_object(def.aux, [Rev.DIFF], 'table-row');

                    var copy_info = get_copy_info(def.revs, nums);

                    for (var i = 0; i < copy_info.length; i++) {
                        var new_el = def.aux.clone().hide().insertAfter(def.aux);
                        clear_rev_marks(new_el);
                        set_number(new_el, copy_info[i].num);
                        tracker.add_object(new_el, copy_info[i].revs, 'table-row');
                    }
                }
            };


            for (var i = 0; i < defs.length; ++i) {
                if (defs[i].type == 's') {
                    finalize_tr(defs[i]);
                } else {
                    finalize_rev_tbody(defs[i]);
                }
            }

            return num_map;
        };

        /** Renumbers and hides the list items according to the given @a num_map
        */
        this.prepare_li = function(num_map) {
            // FIXME: currently we process only the first t-li element out of
            // each block of elements assigned a single num.
            var el_li = $('.t-li1').add($('.t-li2')).add($('.t-li3'));

            var descs = [];
            /*
               { obj: <jQuery object>,
                 obj_num: <jQuery object>
                 num: [<num>, <num>, ...],
               }
            */
            var num_regex = /^\s*(\d+)\s*$/;
            var range_regex = /^\s*(\d+)-(\d+)\s*$/;
            el_li.each(function() {
                var el_num = $(this).children().first('.t-li');
                if (el_num.length == 0) {
                    return;
                }

                var nums = [];
                var items = el_num.text().replace(')','').split(',');
                for (var i = 0; i < items.length; ++i) {
                    var match = items[i].match(num_regex);
                    if (match !== null) {
                        nums.push(parseInt(match[1]));
                        continue;
                    }
                    match = items[i].match(range_regex);
                    if (match !== null) {
                        var first = parseInt(match[1]);
                        var last = parseInt(match[2]);
                        if (first > last) {
                            continue;
                        }
                        for (; first <= last; ++first) {
                            nums.push(first);
                        }
                        continue;
                    }
                }

                if (nums.length != 0) {
                    descs.push({ obj: $(this), nums: nums, obj_num: el_num });
                }
            });


            for (var i = 0; i < descs.length; ++i) {
                var nums = descs[i].nums;

                // get the description of what numbers to display for which
                // revision

                var revs_show = is_shown_fill(true);
                var revs_show_all = true;

                var disp_desc = [];
                var prev_nums = nums;
                var prev_revs = [ Rev.DIFF ];

                for (var rev = Rev.FIRST; rev != Rev.LAST; ++rev) {
                    var target_nums = [];
                    for (var j = 0; j < nums.length; ++j) {
                        if (nums[j] < num_map[rev].length) {
                            var target_num = num_map[rev][nums[j]];
                            if (target_num != -1) {
                                target_nums.push(target_num);
                            }
                        }
                    }

                    if (target_nums.length == 0) {
                        // will hide entire t-liX element
                        revs_show[rev] = false;
                        revs_show_all = false;
                        continue;
                    }

                    if (array_equal(target_nums, prev_nums)) {
                        prev_revs.push(rev);
                    } else {
                        disp_desc.push({ revs: prev_revs, nums: prev_nums });
                        prev_revs = [rev];
                        prev_nums = target_nums;
                    }
                }
                disp_desc.push({ revs: prev_revs, nums: prev_nums });
                // hide entire t-liX element if needed
                if (!revs_show_all) {
                    this.tracker.add_diff_object(descs[i].obj,
                                                 is_shown2revs(revs_show),
                                                 'block');
                }

                // Add t-li elements with different text if needed
                // the first item always includes Rev.DIFF in .revs
                if (disp_desc.length > 1) {
                    this.tracker.add_diff_object(descs[i].obj_num, disp_desc[0].revs,
                                                 'inline-block');
                    for (var j = 1; j < disp_desc.length; ++j) {
                        var new_el = descs[i].obj_num.clone().hide()
                                            .insertAfter(descs[i].obj_num);
                        var text = disp_desc[j].nums[0].toString();
                        // TODO: reduce to ranges
                        for (var k = 1; k < disp_desc[j].nums.length; ++k) {
                            text = text + ',' + disp_desc[j].nums[k].toString();
                        }
                        new_el.text(text + ')');
                        this.tracker.add_object(new_el, disp_desc[j].revs,
                                                'inline-block');
                    }
                }
            }
        };

        this.prepare = function() {
            if (this.is_prepared) {
                return;
            }
            this.prepare_navbar();
            this.prepare_revs();
            this.prepare_dscs();

            var dcl_tables = $('.t-dcl-begin');
            if (dcl_tables.length > 0) {
                var num_map = this.prepare_dcls(dcl_tables.first());
                this.prepare_li(num_map);
            }
            this.is_prepared = true;
        };

        /** Returns an a list of revisions for which a the node should be copied
            and for which revisions each of the copy would be shown.
        */
        this.get_revision_map = function(lines) {
            var res = [];
            res[Rev.DIFF] = [Rev.DIFF];

            var is_shown = [];

            // create separate elements when diff has rev marks
            var is_diff_clean = true;

            lines.each(function() {
                var rev_mark = $(this).find('.t-mark-rev').first();
                is_shown.push(is_shown_on_rev(rev_mark));
                if (rev_mark.length > 0) {
                    is_diff_clean = false;
                }
            });

            // Track the lines shown in the previous revision. If the same lines
            // are shown in the current revision, simply display the element
            // of the previous revision, instead of creating a new one.
            var prev_rev = Rev.DIFF;
            var prev_visible = [];
            if (is_diff_clean) {
                // any further revisions will match this this array only if
                // original version of the element does not contain rev marks
                for (var i = 0; i < is_shown.length; i++) {
                    prev_visible.push(i); // DIFF shows all lines
                }
            }

            for (var rev = Rev.FIRST; rev < Rev.LAST; ++rev) {
                res[rev] = [];

                var curr_visible = [];
                for (var i = 0; i < is_shown.length; i++) {
                    if (is_shown[i][rev] == true) {
                        curr_visible.push(i);
                    }
                }

                if (curr_visible.length == 0) {
                    continue;
                }

                // Maybe nothing has changed from the previous revision and we
                // can simply keep the node created for the previus revision
                if (array_equal(curr_visible, prev_visible)) {
                    res[prev_rev].push(rev);
                } else {
                    res[rev].push(rev);
                    prev_visible = curr_visible;
                    prev_rev = rev;
                }
            }

            return res;
        };

        /** Deletes lines from multi-line links that have marks nearby.
            Returns true if no lines are left. @a titles and @a marks must both
            refer to the children of .t-lines elements.
         */
        this.delete_lines = function(titles, marks, rev) {
            // Delete the lines
            var num_deleted = 0;
            var num_total = titles.length;

            marks.each(function(index) {
                var mark_span = $(this).children('.t-mark-rev');
                if (mark_span.length > 0) {
                    var mark = get_mark(mark_span.first());
                    if (!should_be_shown(rev, mark)) {
                        titles.eq(index).remove();
                        $(this).remove();
                        num_deleted++;
                        return;
                    }
                }
                mark_span.remove(); // delete marks in any case
            });

            // Delete this if empty
            return (num_deleted == num_total);
        };

        /** Creates the standard revision selection box
        */
        this.create_selection_box = function() {
            var head_parent = $('#cpp-head-tools-right');

            this.el.select_div = $('<div/>').addClass('stdrev-select');

            var inner_div = $('<div/>').appendTo(this.el.select_div);
            var span = $('<span/>').addClass('stdrev-text')
                                   .text('Standard revision: ')
                                   .appendTo(inner_div);
            this.el.select = $('<select/>').appendTo(inner_div);

            for (var i = 0; i < desc.length; ++i) {
                $('<option/>').text(desc[i].title)
                              .attr('value', desc[i].rev.toString())
                              .appendTo(this.el.select);
            }

            this.el.select.one('mouseover', this.prepare.bind(this));
            this.el.select.change(this.on_selection_change.bind(this));
            this.el.select_div.prependTo(head_parent);
        };

        /** Callback to be run when the user changes the option selected in the
            selection box
        */
        this.on_selection_change = function() {
            var rev = parseInt(this.el.select.val());
            this.tracker.to_rev(rev);

            // special treatment for rev boxes
            if (this.curr_rev == Rev.DIFF && rev != Rev.DIFF) {
                this.rev_tables.each(function() {
                    $(this).addClass('stdrev-rev-hide');
                });
            }
            if (this.curr_rev != Rev.DIFF && rev == Rev.DIFF) {
                this.rev_tables.each(function() {
                    $(this).removeClass('stdrev-rev-hide');
                });
            }

            this.curr_rev = rev;
        }
    };

    /** Each instance of this class is responsible for versioning either member
        'scopes' (those within {{member}} templates) or the main scope (everything
        what's left)
    */
    function Scope(root, is_main) {

    };

    // get the important elements of the page
    this.get_core_elements = function() {
        this.el.root = $('#mw-content-text');j
        this.el.dcl_tables = this.el.root.find('.t-dcl-begin');
        this.el.dcl_rev_tables = this.el.dcl_tables.filter('.t-dcl-rev-begin');
        this.el.dsc_tables = this.el.root.find('.t-dsc-begin');
        this.el.rev_tables = this.el.root.find('.t-rev-begin');
        this.el.rev_inl_tables = this.el.root.find('.t-rev-inl');
        this.el.list_items = this.el.root.find('.t-li');
    };

    var plugin = new StandardRevisionPlugin();
    plugin.create_selection_box();

});
