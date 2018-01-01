/*
    Copyright (C) 2013-2017  Povilas Kanapickas <povilas@radix.lt>

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


    // Add console.log() if not present
    if (!window.console)
        window.console = {};
    if (!window.console.log)
        window.console.log = function() { };

    var get_url_parameter = function(name) {
        var url = decodeURIComponent(window.location.search.substring(1));
        var params = url.split('&');

        for (i = 0; i < params.length; i++) {
            var param = params[i].split('=');

            if (param[0] === name) {
                return param[1] === undefined ? true : param[1];
            }
        }
        return null;
    };

    var debug = false;
    if (get_url_parameter('stdrev_debug') !== null)
        debug = true;

    // Returns true if the given arrays have the same length and equal elements
    // at specific positions, false otherwise
    function array_equal(a, b) {
        var i = a.length;
        if (i !== b.length) {
            return false;
        }
        while (i--) {
            if (a[i] !== b[i]) {
                return false;
            }
        }
        return true;
    };

    // Given an array of numbers, sorts them, removes non-unique elements and
    // returns the resulting array. The argument array is not modified.
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

    /// Exit if we are not in view mode
    if (mw.config.get('wgAction') != 'view') {
        return;
    }
    if (mw.config.get('wgNamespaceNumber') != 0) {
        return;
    }

    /// Are we dealing with C or C++?
    var is_cxx = (mw.config.get('wgTitle').indexOf('c/') != 0);

    // Standard revision identification 'enums'. Thoughout the plugin it is
    // assumed that the values are integers starting at zero and thus they can
    // be used as an index in regular arrays.
    var Rev_c = {
        DIFF: 0,
        FIRST: 1,
        C89: 1,
        C99: 2,
        C11: 3,
        LAST: 4
    };
    var Rev_cxx = {
        DIFF: 0,
        FIRST: 1,
        CXX98: 1,
        CXX03: 2,
        CXX11: 3,
        CXX14: 4,
        CXX17: 5,
        CXX20: 6,
        LAST: 7,
    };

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
        { rev: Rev.CXX03, title: 'C++98/03' },
        { rev: Rev.CXX11, title: 'C++11' },
        { rev: Rev.CXX14, title: 'C++14' },
        { rev: Rev.CXX17, title: 'C++17' },
        { rev: Rev.CXX20, title: 'C++20' },
    ];

    var rev_css_classes_c = [
        { rev: Rev.C99, since: 't-since-c99', until: 't-until-c99' },
        { rev: Rev.C11, since: 't-since-c11', until: 't-until-c11' },
    ];

    var rev_css_classes_cxx = [
        { rev: Rev.CXX03, since: 't-since-cxx03', until: 't-until-cxx03' },
        { rev: Rev.CXX11, since: 't-since-cxx11', until: 't-until-cxx11' },
        { rev: Rev.CXX14, since: 't-since-cxx14', until: 't-until-cxx14' },
        { rev: Rev.CXX17, since: 't-since-cxx17', until: 't-until-cxx17' },
        { rev: Rev.CXX20, since: 't-since-cxx20', until: 't-until-cxx20' },
    ];

    var desc;
    var rev_css_classes;

    if (is_cxx) {   // select either C or C++ version
        desc = desc_cxx;
        rev_css_classes = rev_css_classes_cxx;
    } else {
        desc = desc_c;
        rev_css_classes = rev_css_classes_c;
    }

    /*  This class stores information about what revisions a certain object
        should be shown on. A number of convenience functions are provided.
    */
    var VisibilityMap = function(revs) {
        this.map = [];

        // initialize the map to "not shown"
        var i;
        for (i = 0; i < Rev.LAST; i++) {
            this.map.push(false);
        }

        if (typeof(revs) !== 'undefined') {
            for (i = 0; i < revs.length; i++) {
                this.map[revs[i]] = true;
            }
        }
    }

    // Checks the visibility on the given revision.
    VisibilityMap.prototype.is_visible_on = function(rev) {
        return this.map[rev];
    }

    // Checks whether all revisions are hidden in this visibility map
    VisibilityMap.prototype.is_visible_on_none = function() {
        for (var i = 0; i < Rev.LAST; i++) {
            if (this.map[i] === true) {
                return false;
            }
        }
        return true;
    }

    // Checks whether all revisions are shown in this visibility map
    VisibilityMap.prototype.is_visible_on_all = function() {
        for (var i = 0; i < Rev.LAST; i++) {
            if (this.map[i] === false) {
                return false;
            }
        }
        return true;
    }

    // Sets the visibility on the given revision to true.
    VisibilityMap.prototype.add = function(rev) {
        this.map[rev] = true;
    }

    // Sets the visibility on the given revision to true.
    VisibilityMap.prototype.remove = function(rev) {
        this.map[rev] = false;
    }


    /*  Fills the visibility map with the given value. After the operation
        map.is_visible_on(rev) == value for all valid revisions.
    */
    VisibilityMap.prototype.fill = function(value) {
        for (var i = 0; i < this.map.length; i++)
            this.map[i] = value;
    }

    var visibility_fill = function(value) {
        var ret = new VisibilityMap();
        ret.fill(value);
        return ret;
    }

    // Clones the visibility map
    VisibilityMap.prototype.clone = function() {
        var ret = new VisibilityMap();
        ret.map = this.map.slice();
        return ret;
    }

    // Checks whether two visibility maps are equal
    VisibilityMap.prototype.equal = function(other) {
        return array_equal(this.map, other.map);
    }

    /*  Combines the map with another visibility map. The resulting map
        indicates visibility on particular revision if both argument maps
        indicated so. Returns this.
    */
    VisibilityMap.prototype.combine_and = function(map) {
        for (var i = 0; i < Rev.LAST; i++) {
            this.map[i] = this.map[i] && map.map[i];
        }
    }

    /*  Combines the map with another visibility map. The resulting map
        indicates visibility on particular revision if either argument maps
        indicated so.
    */
    VisibilityMap.prototype.combine_or = function(map) {
        for (var i = 0; i < Rev.LAST; i++) {
            this.map[i] = this.map[i] || map.map[i];
        }
    }

    // Prints the contents to a string
    VisibilityMap.prototype.debug_to_string = function() {
        var out = '{ ';
        for (var i = 0; i < this.map.length; i++) {
            if (this.map[i]) {
                out += 'T';
            } else {
                out += 'F';
            }
        }
        out += ' }';
        return out;
    }

    /*  Given an jQuery object, inspects mark css classes and returns a
        visibility map corresponding to these css classes. Rev.DIFF is not
        included into the returned visibility map.
    */
    function get_visibility_map(el) {
        var map = new VisibilityMap();
        for (var i = 0; i < rev_css_classes.length; i++) {
            if (el.hasClass(rev_css_classes[i].since)) {
                break;
            }
        }
        if (i === rev_css_classes.length) {
            map.add(Rev.FIRST);
            i = 0;
        }
        for (; i < rev_css_classes.length; i++) {
            if (el.hasClass(rev_css_classes[i].until)) {
                break;
            }
            map.add(rev_css_classes[i].rev);
        }
        return map;
    }

    /** This class keeps track of objects that need to be shown or hidden for
        specific standard revision.
    */
    var ObjectTracker = function() {

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
    }

    /** Adds a jQuery object @a obj that should be shown only on specific
        revisions identified by @a revs. @a orig_obj is used to compute the
        display property that should be set to the object when the visibility
        is restored.
    */
    ObjectTracker.prototype.add_object = function(obj, orig_obj, visibility_map) {
        var id = this.all_objects.length;
        this.all_objects[id] = obj;
        this.all_display[id] = orig_obj.css('display');

        for (var rev = 0; rev < Rev.LAST; rev++) {
            if (visibility_map.is_visible_on(rev)) {
                this.rev2id_map[rev].push(id);
            }
        }
    };

    // Same as add_object except that obj is used to compute the display
    // property. The object must be already attached to DOM.
    ObjectTracker.prototype.add_diff_object = function(obj, visibility_map) {
        this.add_object(obj, obj, visibility_map);
    }

    /*  Changes the visibility of objects to what it should be at the given
        revision rev.
    */
    ObjectTracker.prototype.to_rev = function(rev) {
        if (rev === this.curr_rev) {
            return;
        }
        var visible_before = this.rev2id_map[this.curr_rev];
        var visible_after = this.rev2id_map[rev];

        var i, curr;
        for (i = 0; i < visible_before.length; ++i) {
            curr = visible_before[i];
            if ($.inArray(curr, visible_after) === -1) {
                this.all_objects[curr].css('display', 'none');
            }
        }
        for (i = 0; i < visible_after.length; ++i) {
            curr = visible_after[i];
            if ($.inArray(curr, visible_before) === -1) {
                this.all_objects[curr].css('display', this.all_display[curr]);
            }
        }
        this.curr_rev = rev;
    };

    /*  This class tracks object visibility throughout the section hierarchy.
        For example, when section contents are not visible on a certain
        revision, then related visual objects such as section title are hidden
        too.

        In the context of this class, visual objects can be of one of the
        following four kinds: primary, secondary, heading, unknown and
        container. A visual object is a certain DOM node in the tree. Section
        boundaries and hierarchy has no relation to the DOM hierarchy.

            Primary

        Primary objects define the visibility of the whole section the objects
        are in. If all primary and unknown objects are not visible, the whole
        section is hidden. The reason why unknown objects affect the visibility
        of sections is that we want to be conservative and if we can't
        determine the kind of an object, better treat it as primary.

        Primary objects do not contain other objects.

            Secondary

        Secondary objects don't affect the visibility of sections if there are
        primary on unknown elements in it. If the section contains only
        secondary elements, it is are hidden if all secondary elements are
        hidden.

        Secondary objects do not contain other objects.

            Heading

        Heading elements never affect the visibility of sections. All other
        elements in the section are hidden, headings are hidden too.

            Container

        Container objects contain other visual objects and add some visual
        "effect" such as padding, so that in order to hide the presence
        of the contained objects completely, the container must be hidden too.

            Unknown

        Unknown objects are those objects for which any other kind was not
        defined. They are treated the same way as primary objects.

        Unknown objects do not contain other objects.


        When all primary and unknown elements within a section are not visible
        in certain revision, then all secondary elements are hidden too. The
        process is repeated throughout entire section hierarchy.

        The section hierarchy tree is built by specifying hierarchy level via
        set_level() and adding elements via add_*() functions. Hierarchy levels
        are identified by ascending integer numbers. Container objects are set
        independently via enter_container() and exit_container() functions -
        these functions effectively form a parallel hierarchy.
    */
    var SectionContentsTracker = function() {
        this.root_section = new SectionNode(null);
        this.root_container = new ContainerNode(null, null);
        this.curr_section = this.root_section;
        this.curr_container = this.root_container;
    };

    var ObjectType = {
        PRIMARY : 0,
        SECONDARY : 1,
        HEADING : 2,
        UNKNOWN : 3,
        SECTION : 4,
        CONTAINER : 5
    };

    // internal classes for SectionContentsTracker
    var ObjectNode = function(parent_section, parent_container, type, obj) {
        this.parent_section = parent_section;
        this.parent_container = parent_container;
        this.level = parent_section.level + 1;
        this.children = null;
        this.obj = obj;
        this.type = type;
        this.visible = null;
    };

    // Creates a section node given a parent node. For root section parent
    // should be null. The level of the created section is determined
    // automatically from the level of the parent section.
    var SectionNode = function(parent) {
        this.parent_section = parent;
        if (parent === null) {
            this.level = 0;
        } else {
            this.level = this.parent_section.level + 1;
        }
        this.children = [];
        this.obj = null;
        this.type = ObjectType.SECTION;
        this.visible = null;
    };

    // Creates a container node given a parent container and the jQuery object
    // representing the object. For root container parent should be null.
    var ContainerNode = function(parent, obj) {
        this.parent_container = parent;
        this.children = [];
        this.obj = obj;
        this.type = ObjectType.CONTAINER;
        this.visible = null;
    };

    /*  Walks the internal section hierarchy tree to the specified level. If
        level is higher than current level, then new section nodes are created as
        descendants of the current section node. If the current level is the
        same, a new node is created.

        Sections are portions of the html tree delimited by the heading
        elements (<h1>, <h2>, etc.)
    */
    SectionContentsTracker.prototype.set_level = function(level) {
        if (level < 0) {
            console.log("Level must be positive");
            return;
        }

        while (this.curr_section.level >= level && this.curr_section.level > 0) {
            this.curr_section = this.curr_section.parent_section;
        }
        while (this.curr_section.level < level) {
            var new_section = new SectionNode(this.curr_section);
            this.curr_section.children.push(new_section);
            this.curr_section = new_section;
        }
    };

    /*  Adds an jQuery object to the current section and container. type is the
        kind of the object and visible is the visibility map. Don't use this
        method, use add_primary, add_secondary and add_unknown instead
    */
    SectionContentsTracker.prototype.add_object = function(obj, type, visible) {
        var new_node = new ObjectNode(this.curr_section, this.curr_container, type, obj);
        new_node.visible = visible;
        this.curr_section.children.push(new_node);
        this.curr_container.children.push(new_node);
    };

    // Adds a primary object to the current section and container with the
    // given visibility map.
    SectionContentsTracker.prototype.add_primary = function(obj, visible) {
        this.add_object(obj, ObjectType.PRIMARY, visible);
    };

    // Adds a secondary object to the current section and container
    SectionContentsTracker.prototype.add_secondary = function(obj, visible) {
        this.add_object(obj, ObjectType.SECONDARY, visible);
    };

    // Adds a heading object to the current section and container
    SectionContentsTracker.prototype.add_heading = function(obj) {
        this.add_object(obj, ObjectType.HEADING, null);
    };

    // Adds an unknown object to the current section and container
    SectionContentsTracker.prototype.add_unknown = function(obj) {
        this.add_object(obj, ObjectType.UNKNOWN, visibility_fill(true));
    };

    // Interprets a given object as a container and "enters" it. From this call
    // until call to exit_container, all added objects are added as descendants
    // of this container. Multiple containers may be nested.
    SectionContentsTracker.prototype.enter_container = function(obj) {
        var new_node = new ContainerNode(this.curr_container, obj);
        this.curr_container.children.push(new_node);
        this.curr_container = new_node;
    };

    SectionContentsTracker.prototype.exit_container = function() {
        this.curr_container = this.curr_container.parent_container;
    };

    // Recursively evaluates visibility of a section object
    SectionContentsTracker.prototype.eval_section_visibility = function(obj) {
        var visible = new VisibilityMap();
        var secondary_visible = new VisibilityMap();
        var i, child;
        var has_non_secondary = false;

        for (i = 0; i < obj.children.length; i++) {
            child = obj.children[i];
            switch (child.type) {
            case ObjectType.PRIMARY:
            case ObjectType.UNKNOWN:
                visible.combine_or(child.visible);
                has_non_secondary = true;
                break;
            case ObjectType.SECONDARY:
                secondary_visible.combine_or(child.visible);
                break;
            case ObjectType.HEADING:
                break;
            case ObjectType.SECTION:
                visible.combine_or(this.eval_section_visibility(child));
                has_non_secondary = true;
                break;
            }
        }

        if (has_non_secondary) {
            // Apply the resolved visibility to secondary children elements, if any
            for (i = 0; i < obj.children.length; i++) {
                child = obj.children[i];
                if (child.type === ObjectType.SECONDARY) {
                    child.visible = visible;
                }
            }
        } else {
            visible = secondary_visible;
        }

        // Apply the resolved visibility to heading children elements, if any
        for (i = 0; i < obj.children.length; i++) {
            child = obj.children[i];
            if (child.type === ObjectType.HEADING) {
                child.visible = visible;
            }
        }

        obj.visible = visible;
        return visible;
    };

    // Recursively evaluates visibility of container objects. Assumes that
    // visibility of secondary objects is already set
    SectionContentsTracker.prototype.eval_container_visibility = function(obj) {
        var visible = new VisibilityMap();
        for (var i = 0; i < obj.children.length; i++) {
            var child = obj.children[i];
            if (child.type === ObjectType.CONTAINER) {
                visible.combine_or(this.eval_container_visibility(child));
            } else {
                visible.combine_or(child.visible);
            }
        }
        obj.visible = visible;
        return visible;
    };

    /*  Checks if the object needs to be hidden in any revisions identified in
        mask and if yes, performs the hide operation. visible_mask is a
        visibility map. Returns the visibility of the object ANDed with the mask.
    */
    SectionContentsTracker.prototype.perform_hide_obj =  function(obj, tracker, visible_mask) {
        var wanted_visible = obj.visible.clone();
        wanted_visible.combine_and(visible_mask);
        if (!wanted_visible.equal(visible_mask)) {
            tracker.add_diff_object(obj.obj, wanted_visible);
            return wanted_visible;
        }
        return visible_mask;
    };

    // Recursively evaluates the contents of a container and hides container,
    // heading and secondary elements if needed. visible_mask identifies which
    // revisions the object may be visible in certain revision (it may not be
    // visible in case parent container is not visible).
    SectionContentsTracker.prototype.perform_hide = function(obj, tracker, visible_mask) {
        // handle visibility of the container
        if (obj !== this.root_container) {
            visible_mask = this.perform_hide_obj(obj, tracker, visible_mask);
        }

        // handle visibility of contents
        for (var i = 0; i < obj.children.length; ++i) {
            var child = obj.children[i];
            switch (child.type) {
            case ObjectType.CONTAINER:
                this.perform_hide(child, tracker, visible_mask);
                break;
            case ObjectType.SECONDARY:
            case ObjectType.HEADING:
                this.perform_hide_obj(child, tracker, visible_mask);
                break;
            }
        }
    };

    SectionContentsTracker.prototype.debug_obj_impl =
            function(obj, desc, level) {
        // note that obj.level only considers section hierarchy. When printing
        // container hierarchy the depth level will be different and must be
        // calculated explicitly
        var indent = ' '.repeat(level);
        var tag = '';
        if (obj.obj !== null)
            tag = obj.obj.prop("tagName");

        return indent + desc + ' ' + tag + '\n';
    };

    SectionContentsTracker.prototype.debug_obj = function(obj, level) {
        switch (obj.type) {
        case ObjectType.PRIMARY:
            return this.debug_obj_impl(obj, 'primary object', level);
        case ObjectType.SECONDARY:
            return this.debug_obj_impl(obj, 'secondary object', level);
        case ObjectType.UNKNOWN:
            return this.debug_obj_impl(obj, 'unknown object', level);
        case ObjectType.HEADING:
            return this.debug_obj_impl(obj, 'heading object', level);
        }
        return '';
    };

    SectionContentsTracker.prototype.debug_section_obj = function(obj, level) {
        if (obj.type === ObjectType.SECTION) {
            var out = this.debug_obj_impl(obj, 'section', level);
            for (var i = 0; i < obj.children.length; ++i) {
                out += this.debug_section_obj(obj.children[i], level+1);
            }
            return out;
        }
        return this.debug_obj(obj, level);
    };

    SectionContentsTracker.prototype.debug_container_obj = function(obj, level) {
        if (obj.type === ObjectType.CONTAINER) {
            var out = this.debug_obj_impl(obj, 'container', level);
            for (var i = 0; i < obj.children.length; ++i) {
                out += this.debug_container_obj(obj.children[i], level+1);
            }
            return out;
        }
        return this.debug_obj(obj, level);
    };

    SectionContentsTracker.prototype.debug_all = function() {
        var out = 'Section hierarchy:\n\n';
        out += this.debug_section_obj(this.root_section, 0);
        out += '\nContainer hierarchy:\n\n';
        out += this.debug_container_obj(this.root_container, 0);
        return out;
    };

    SectionContentsTracker.prototype.run = function(tracker) {
        // evaluate visibility of sections and containers
        this.eval_section_visibility(this.root_section);
        this.eval_container_visibility(this.root_container);

        this.perform_hide(this.root_container, tracker, visibility_fill(true));

        if (debug) {
            alert(this.debug_all());
        }
    };

    /*  Used to aggregate a set of objects that need to be versioned. The set
        may be created from objects only in certain part of the DOM tree, this
        allows to perform independent versioning execution in different parts
        of the page.

        This is used for example to support inclusions of Template:member. It
        almost always contains a separate set declaration and description lists
        whose numbering needs to be versioned separately.
    */
    var Scope = function(root) {
        this.root = root;
    };

    /** Creates a new scope and initializes it with the objects gathered from
        the given jQuery object. Returns the new scope.
    */
    Scope.create_root = function(obj) {
        var scope = new Scope(obj);
        scope.nv = scope.root.find('.t-navbar');
        scope.dcl_tables = scope.root.find('.t-dcl-begin');
        scope.dcl_rev_tables = scope.dcl_tables.filter('.t-dcl-rev-begin');
        scope.rev_tables = scope.root.find('.t-rev-begin');
        scope.rev_inl_tables = scope.root.find('.t-rev-inl');
        scope.list_items = scope.root.find('.t-li1');
        scope.list_items.add(scope.root.find('.t-li2'));
        scope.list_items.add(scope.root.find('.t-li3'));
        return scope;
    };

    /** Given two scopes: parent scope and child scope, moves the elements
        contained within jQuery object in parent_scope[prop] to
        child_scope[prop] whenever they have child_scope.root as parent.
    */
    Scope.split_scope = function(parent_scope, child_scope, prop) {

        // get elements to move
        var to_move = parent_scope[prop].filter(function() {
            return $.contains(child_scope.root[0], this);
        });

        // remove elements from parent and add to child
        parent_scope[prop] = parent_scope[prop].not(to_move);
        child_scope[prop] = to_move;
    };

    /** Creates a new scope and initializes it with the objects from the given
        parent scope that also have the given jQuery object obj as parent. The
        filtered objects are removed from the parent scope. The function returns
        the new scope.
    */
    Scope.create_child = function(parent, obj) {
        var scope = new Scope(obj);
        Scope.split_scope(parent, scope, 'nv');
        Scope.split_scope(parent, scope, 'dcl_tables');
        Scope.split_scope(parent, scope, 'dcl_rev_tables');
        Scope.split_scope(parent, scope, 'rev_tables');
        Scope.split_scope(parent, scope, 'rev_inl_tables');
        Scope.split_scope(parent, scope, 'list_items');
        return scope;
    };

    var StandardRevisionPlugin = function() {
        this.curr_rev = Rev.DIFF;

        this.tracker = new ObjectTracker();
        this.is_prepared = false;
    };

    /*  Prepares the navbar for versioning using object tracker. As the navbar
        contains many items and we might want to reflow the columns in the
        future, instead of committing each item to the object tracker we make
        as many copies of the original navbar as there needed, customize each
        copy in-place and commit the results to the object tracker. This gives
        us both performance and flexibility benefits.
    */
    StandardRevisionPlugin.prototype.prepare_navbar = function(scope) {
        var nv = scope.nv // main navbar
        if (nv.length === 0) {
            return; // no navbar
        }

        this.tracker.add_diff_object(nv, new VisibilityMap([Rev.DIFF]));

        var self = this;

        for (var rev = Rev.FIRST; rev < Rev.LAST; ++rev) {
            // Create new navbar and insert it to the tracker
            var rev_nv = nv.clone().hide().insertAfter(nv);
            this.tracker.add_object(rev_nv, nv, new VisibilityMap([rev]));

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
                var marks;

                if (link_tds.length === 0) {
                    // bare nv template used. Check if we don't have a mark
                    // template by chance
                    marks = $(this).find('.t-mark-rev');
                    if (marks.length > 0) {
                        var visible = get_visibility_map(marks.first());
                        visible.add(Rev.DIFF);
                        if (!visible.is_visible_on(rev)) {
                            $(this).remove();
                        } else {
                            marks.remove(); // do not show marks in any case
                        }
                    }
                    return;
                }

                if (link_tds.length === 1) {
                    // The earliest standard (always visible)
                    return;
                }
                var titles = link_tds.first().children().children().first().children();
                marks = link_tds.last().children().first().children();

                // Delete the lines
                if (self.delete_lines(titles, marks, rev)) {
                    $(this).remove();
                }
            });

            // Remove all empty column tables
            el_col_tables.each(function() {
                if ($(this).find('.t-nv').length === 0) {
                    $(this).remove();
                }
            });

            // Look for any headings that do not have items after them
            el_h2.each(function() {
                if ($(this).next().length === 0 ||
                    $(this).next().is('.t-nv-h2, .t-nv-h1')
                ) {
                    $(this).remove();
                }
            });

            el_h1.each(function() {
                if ($(this).next().length === 0 ||
                    $(this).next().is('.t-nv-h1')
                ) {
                    $(this).remove();
                }
            });

            // TODO: perhaps it's worth to reflow the remaining columns
        }
    };

    /*  Handles inclusion of Template:rev_begin, Template:rev and
        Template:rev_end.

        We don't copy the contents of this templates around. We just add the
        rows to the element tracker and show and hide them as needed. To hide
        the frame on non-diff revisions, we have special treatment in
        on_selection_change. Note, that in order for this to work, the revision
        marks must not be touched.

        The visibility map of whole table is stored as 'visible' data member
        of the jquery element.
    */
    StandardRevisionPlugin.prototype.prepare_rev = function(el) {
        var rev_elems = el.children('tbody').children('.t-rev');
        var self = this;
        var table_visible = new VisibilityMap();

        rev_elems.each(function() {
            var visible = get_visibility_map($(this));
            visible.add(Rev.DIFF);
            table_visible.combine_or(visible);

            self.tracker.add_diff_object($(this), visible);
        });
        el.data('visible', table_visible);
    };

    StandardRevisionPlugin.prototype.prepare_all_revs = function(scope) {
        var self = this;
        scope.rev_tables.each(function() {
            self.prepare_rev($(this));
        });
    };

    /** Handles inclusions of Template:rev_inl
    */
    StandardRevisionPlugin.prototype.prepare_all_inl_revs = function(scope) {
        var self = this;
        scope.rev_inl_tables.each(function() {
            self.tracker.add_diff_object($(this), new VisibilityMap([Rev.DIFF]));

            var visible = get_visibility_map($(this));
            var copy = $(this).children().first().clone().hide()
                              .insertAfter($(this));

            self.tracker.add_object(copy, $(this), visible);
        });
    };

    // Returns true if the given jQuery object defines a secondary visual object
    StandardRevisionPlugin.prototype.is_secondary = function(el) {
        if (el.is('p') ||
            el.is('.t-rev-begin'))
        {
            return true;
        }
        return false;
    };

    // Returns true if the given jQuery object defines a heading visual object
    StandardRevisionPlugin.prototype.is_heading = function(el) {
        if (el.is('h2') ||
            el.is('h3') ||
            el.is('h5') ||
            (el.is('tr') && el.has('td > h5').length) ||
            el.is('.t-dsc-header'))
        {
            return true;
        }
        return false;
    };

    /*  If the given jQuery object refers to a heading element, then returns
        the section level for that heading. More "important" heading elements
        have lower section levels, the lowest being 0. If the given jQuery
        object does not refer to a heading, then the function returns -1.
    */
    StandardRevisionPlugin.prototype.get_heading_level = function(el) {
        if (el.is('h2'))
            return 0;
        if (el.is('h3'))
            return 1;
        if (el.is('h5'))
            return 2;
        if (el.is('tr') && el.has('td > h5').length)
            return 2;
        if (el.is('.t-dsc-header'))
            return 3;
        return -1;
    }

    /*  If jQuery object el has a known section level, then we enter that
        section level by exiting section nodes or creating new section nodes
        and entering them as needed.
    */
    StandardRevisionPlugin.prototype.set_level_if_needed = function(section_tracker, el) {
        var level = this.get_heading_level(el);
        if (level >= 0) {
            section_tracker.set_level(level);
        }
    };

    /*  Handles the section hierarchy in a scope as defined by description
        lists and their contents. Description lists are inclusions of
        Template:dsc_* ('t-dsc-*' CSS classes).
        See the documentation of SectionContentsTracker for more information.

        Also prepares items in dsc lists
    */
    StandardRevisionPlugin.prototype.prepare_sections_and_dscs = function(scope) {
        var self = this;

        var section_tracker = new SectionContentsTracker();

        scope.root.children().each(function(){
            var el = $(this);
            if (el.hasClass('t-dsc-begin')) {
                // currently this is the only element that may contain primary
                // elements. Note that the set of primary elements may be
                // expanded in the future.
                self.prepare_dsc_table(section_tracker, el);
            } else if (self.is_secondary(el)) {
                if (el.is('.t-rev-begin')) {
                    section_tracker.add_secondary(el, el.data('visible'));
                } else {
                    section_tracker.add_secondary(el, visibility_fill(true));
                }
            } else if (self.is_heading(el)) {
                self.set_level_if_needed(section_tracker, el);
                section_tracker.add_heading(el);
            } else {
                section_tracker.add_unknown(el);
            }
        });
        section_tracker.run(this.tracker);
    };

    // Handles a description list
    StandardRevisionPlugin.prototype.prepare_dsc_table = function(section_tracker, el) {
        section_tracker.enter_container(el);

        var rows = el.children('tbody').children();
        var self = this;
        rows.each(function() {
            var el = $(this);
            if (el.is('.t-dsc')) {
                section_tracker.add_primary(el, self.prepare_dsc(el));
            } else if (self.is_secondary(el)) {
                section_tracker.add_secondary(el, visibility_fill(true));
            } else if (self.is_heading(el)) {
                self.set_level_if_needed(section_tracker, el);
                section_tracker.add_heading(el);
            } else {
                section_tracker.add_unknown(el);
            }
        });
        section_tracker.exit_container();
    };

    /*  Handles one description list item (inclusion of Template:dsc_*,
        't-dsc-*' CSS classes).

        Returns a visibility map for that item.
    */
    StandardRevisionPlugin.prototype.prepare_dsc = function(el) {
        var self = this;

        /*  Handles the case one of the specialized wrapper templates is
            used. This case is special in that the description may contain
            several names, each with standard tag attached.
        */
        function process_dsc_specialized(el, member) {
            var lines = member.find('.t-lines');
            if (lines.length !== 2) {
                return visibility_fill(true);
            }
            var marks = lines.last();

            var rev_map = self.get_revision_map(marks.children());
            self.tracker.add_diff_object(el, rev_map[Rev.DIFF]);

            for (var rev = Rev.FIRST; rev < Rev.LAST; ++rev) {
                if (rev_map[rev].is_visible_on_none()) {
                    continue;
                }

                var copy = el.clone().hide();
                self.tracker.add_object(copy, el, rev_map[rev]);

                member = copy.children().children('.t-dsc-member-div');
                lines = member.find('.t-lines');
                var titles = lines.first().children();
                marks = lines.last().children();

                self.delete_lines(titles, marks, rev);
                copy.insertAfter(el);
            }
            return self.revision_map_to_visibility(rev_map);
        };

        // Handles the generic dsc template case
        function process_dsc_generic(el) {
            var td = el.children().first();
            if (td.find('.t-mark-rev').length === 0) {
                return visibility_fill(true);
            }
            var rev_map = self.get_revision_map(td);
            self.tracker.add_diff_object(el, rev_map[Rev.DIFF]);

            for (var rev = Rev.FIRST; rev < Rev.LAST; ++rev) {
                if (rev_map[rev].is_visible_on_none()) {
                    continue;
                }

                var copy = el.clone().hide();
                self.tracker.add_object(copy, el, rev_map[rev]);
                // remove marks, but only in the first column
                copy.children().first().find('.t-mark-rev').remove();
                copy.insertAfter(el);
            }
            return self.revision_map_to_visibility(rev_map);
        };

        var member = el.children().children('.t-dsc-member-div');
        if (member.length !== 0) {
            return process_dsc_specialized(el, member);
        } else {
            return process_dsc_generic(el);
        }
    };

    /** Handles declaration tables and their contents. These are implemented
        by including Template:dcl_* templates ('t-dcl-*' CSS classes)

        Returns "numbering map", which defines how the list items are
        renumbered (or deleted) for each revision. The numbering map is a an
        two-dimensional array - the first index identifies the revision,
        the second -- original number. The value obtained this way
        identifies whether the entry should be hidden and if not, what
        version number should be displayed on the specific revision. Hidden
        entry is identified by -1.

        array[revision][orig_num] -> target_num or -1
    */
    StandardRevisionPlugin.prototype.prepare_all_dcls = function(dcl_table) {

        var tracker = this.tracker;

        // get abstract description of the contents
        defs = [];

        /*
            <Simple dcl> :== {
                type: 'i',
                obj: <jQuery object>
                revs: <visibility map>,

                // -1 if not defined
                num: 'orig_num'
            }

            <Rev-list dcl> :== {
                type: 'r',
                obj: <jQuery object>,
                revs: <visibility map>',
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
                revs: visibility_fill(true)
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
                    new_def.revs = get_visibility_map(el);
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
                revs: visibility_fill(true),
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
                    new_def.revs = get_visibility_map(el);
                    has_revs = true;
                }
            }

            // process the member dcls
            el.children('.t-dcl').each(function() {
                var new_id = process_tr($(this), has_num, has_revs,
                                        new_def.revs.clone());
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

        // Prints defs to a string
        function debug_print_defs(defs) {
            var out = '';
            for (var i = 0; i < defs.length; i++) {
                out += ' { i:' + i + ' type:' + defs[i].type + ' num:' + defs[i].num;
                out += ' visible:' + defs[i].revs.debug_to_string();
                if (defs[i].type === 'r') {
                    out += ' { ';
                    for (var j = 0 ; j < defs[i].children.length; ++j) {
                        out += defs[i].children[j] + ' ';
                    }
                    out += '}';
                }
                out += ' }\n';
            }
            return out;
        }

        /* Get the mapping between revisions and function version numbers.
           The function returns an array:

           array[revision][source version number] -> version number to display
        */
        function get_num_map() {
            var num_map = [];

            // We need the maximum visible num to initialize the result array
            // properly
            var max_num = -1;
            var i;
            for (i = 0; i < defs.length; ++i) {
                if (defs[i].num > max_num) {
                    max_num = defs[i].num;
                }
            }

            if (max_num > -1) {

                for (var rev = Rev.FIRST; rev !== Rev.LAST; ++rev) {

                    var visible_nums = [];

                    for (i = 0; i < defs.length; ++i) {
                        if (defs[i].revs.is_visible_on(rev) &&
                            defs[i].num !== -1) {
                            visible_nums.push(defs[i].num);
                        }
                    }

                    visible_nums = array_sort_unique(visible_nums);

                    var curr_map = [-1];
                    for (var num = 1; num <= max_num; ++num) {
                        curr_map[num] = -1;
                    }

                    var curr_num = 1;
                    for (i = 0; i < visible_nums.length; ++i) {
                        curr_map[visible_nums[i]] = curr_num;
                        curr_num++;
                    }
                    num_map[rev] = curr_map;
                }
            }
            return num_map;
        };

        // Prints num_map to a string
        function debug_print_num_map(num_map) {
            var out = '';
            for (var rev = Rev.FIRST; rev !== Rev.LAST; ++rev) {
                out += '[' + desc[rev].title + ']: { ';
                out +=  num_map[rev] + ' }\n';
            }
            return out;
        }

        var num_map = get_num_map();

        if (debug) {
            alert(debug_print_defs(defs) + '\n\n' +
                  debug_print_num_map(num_map));
        }

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
            for (var rev = Rev.FIRST; rev !== Rev.LAST; ++rev) {
                nums[rev] = num_map[rev][num];
            }
            return nums;
        };

        /*  Returns a visibility map that identifies whether any children of
            rev-list identified by def are shown on particular revision.
        */
        function any_children_visible_on_rev(def) {
            var ret = new VisibilityMap();

            for (var i = 0; i !== def.children.length; ++i) {
                ret.combine_or(defs[def.children[i]].revs);
            }
            ret.remove(Rev.DIFF);
            return ret;
        };

        /** Returns infomation about the required copies of the base
            element.
        */
        function get_copy_info(visible, nums) {
            var res = [];

            var base_rev;   // Don't create a new element if it would
            var new_num;    // be identical to previous one
            var new_visible;
            var is_first = true;

            for (var rev = Rev.FIRST; rev !== Rev.LAST; ++rev) {
                if (!visible.is_visible_on(rev)) {
                    continue;
                }
                if (!is_first && new_num === nums[rev]) {
                    // Identical element already exists
                    new_visible.add(rev);
                    continue;
                }

                if (!is_first) {
                    res.push({ base_rev: base_rev, revs: new_visible,
                               num: new_num });
                }

                base_rev = rev;
                new_num = nums[rev];
                new_visible = new VisibilityMap([rev]);
                is_first = false;
            }
            if (!is_first) {
                res.push({ base_rev: base_rev, revs: new_visible,
                           num: new_num });
            }
            return res;
        };

        function finalize_tr(def) {
            var new_el;
            if (def.num === -1) {
                if (def.revs.is_visible_on(Rev.DIFF)) {
                    // no num and no rev-marks -- shown always
                    tracker.add_diff_object(def.obj, def.revs);
                } else {
                    // no num -- two versions: one with rev-marks and
                    // one without
                    new_el = def.obj.clone().hide().insertAfter(def.obj);
                    clear_rev_marks(new_el);
                    tracker.add_diff_object(def.obj, new VisibilityMap([Rev.DIFF]));
                    tracker.add_object(new_el, def.obj, def.revs);
                }
            } else {
                // need to handle numbering
                var nums = get_tr_nums(def.num);

                tracker.add_diff_object(def.obj, new VisibilityMap([Rev.DIFF]));

                var copy_info = get_copy_info(def.revs, nums);

                for (var i = 0; i < copy_info.length; i++) {
                    new_el = def.obj.clone().hide().insertAfter(def.obj);
                    clear_rev_marks(new_el);
                    set_number(new_el, copy_info[i].num);
                    tracker.add_object(new_el, def.obj, copy_info[i].revs);
                }
            }
        };

        /*  Roughly the same as finalize_tr, but while all modifications are
            applied to the t-dcl-rev-aux element, we hide entire tbody
            section when it has no contents or defs[i].revs.is_visible_on(rev)
            is false
        */
        function finalize_rev_tbody(def) {
            // The rev-list tbody does not ever change - we only need to
            // hide it sometimes
            var tbody_visible = def.revs.clone();
            tbody_visible.combine_and(any_children_visible_on_rev(def));
            tbody_visible.add(Rev.DIFF);
            tracker.add_diff_object(def.obj, tbody_visible);
            var new_el;

            if (def.num === -1) {
                if (def.revs.is_visible_on(Rev.DIFF)) {
                    // No num and no rev-marks -- no further modifications
                    // needed.

                } else {
                    // No num -- two versions: one with rev-marks and
                    // one without
                    new_el = def.aux.clone().hide().insertAfter(def.aux);
                    clear_rev_marks(new_el);
                    tracker.add_diff_object(def.aux, new VisibilityMap([Rev.DIFF]));

                    var aux_visible = tbody_visible; // no need to clone
                    aux_visible.remove(Rev.DIFF);
                    tracker.add_object(new_el, def.aux, aux_visible);
                }
            } else {
                // need to handle numbering
                var nums = get_tr_nums(def.num);

                tracker.add_diff_object(def.aux, new VisibilityMap([Rev.DIFF]));

                var copy_info = get_copy_info(def.revs, nums);

                for (var i = 0; i < copy_info.length; i++) {
                    new_el = def.aux.clone().hide().insertAfter(def.aux);
                    clear_rev_marks(new_el);
                    set_number(new_el, copy_info[i].num);
                    tracker.add_object(new_el, def.aux, copy_info[i].revs);
                }
            }
        };


        for (var i = 0; i < defs.length; ++i) {
            if (defs[i].type === 's') {
                finalize_tr(defs[i]);
            } else {
                finalize_rev_tbody(defs[i]);
            }
        }

        return num_map;
    };

    /** Renumbers and hides the list items according to the given @a num_map
    */
    StandardRevisionPlugin.prototype.prepare_all_li = function(scope, num_map) {
        // FIXME: currently we process only the first t-li element out of
        // each block of elements assigned a single num.
        var descs = [];
        /*
           { obj: <jQuery object>,
             obj_num: <jQuery object>
             num: [<num>, <num>, ...],
           }
        */
        var num_regex = /^\s*(\d+)\s*$/;
        var range_regex = /^\s*(\d+)-(\d+)\s*$/;
        scope.list_items.each(function() {
            var el_num = $(this).children().first('.t-li');
            if (el_num.length === 0) {
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

            var visible = visibility_fill(true);

            var disp_desc = [];
            var prev_nums = nums;
            var prev_visible = new VisibilityMap([Rev.DIFF]);

            for (var rev = Rev.FIRST; rev !== Rev.LAST; ++rev) {
                var target_nums = [];
                for (var j = 0; j < nums.length; ++j) {
                    if (nums[j] < num_map[rev].length) {
                        var target_num = num_map[rev][nums[j]];
                        if (target_num !== -1) {
                            target_nums.push(target_num);
                        }
                    }
                }

                if (target_nums.length === 0) {
                    // will hide entire t-liX element
                    visible.remove(rev);
                    continue;
                }

                if (array_equal(target_nums, prev_nums)) {
                    prev_visible.add(rev);
                } else {
                    disp_desc.push({ visible: prev_visible, nums: prev_nums });
                    prev_visible = new VisibilityMap([rev]);
                    prev_nums = target_nums;
                }
            }
            disp_desc.push({ visible: prev_visible, nums: prev_nums });
            // hide entire t-liX element if needed
            if (!visible.is_visible_on_all()) {
                this.tracker.add_diff_object(descs[i].obj, visible);
            }

            // Add t-li elements with different text if needed
            // the first item always includes Rev.DIFF in .revs
            if (disp_desc.length > 1) {
                this.tracker.add_diff_object(descs[i].obj_num, disp_desc[0].visible);
                for (var j = 1; j < disp_desc.length; ++j) {
                    var new_el = descs[i].obj_num.clone().hide()
                                        .insertAfter(descs[i].obj_num);
                    var text = disp_desc[j].nums[0].toString();
                    // TODO: reduce to ranges
                    for (var k = 1; k < disp_desc[j].nums.length; ++k) {
                        text = text + ',' + disp_desc[j].nums[k].toString();
                    }
                    new_el.text(text + ')');
                    this.tracker.add_object(new_el, descs[i].obj_num, disp_desc[j].visible);
                }
            }
        }
    };

    // An utility function that calls fun on all known scopes
    StandardRevisionPlugin.prototype.for_all_scopes = function(fun) {
        fun.call(this.root_scope);
        for (var i = 0; i < this.child_scopes.length; ++i) {
            fun.call(this.child_scopes[i]);
        }
    };

    /*  An utility function that gathers information about visible objects and
        pushes it to various internal trackers. New DOM objects may be created
        and others deleted, but the visual appearance should not change.
    */
    StandardRevisionPlugin.prototype.prepare = function() {
        if (this.is_prepared) {
            return;
        }

        // initialize scopes
        this.root_scope = Scope.create_root($('#mw-content-text').first());
        this.child_scopes = [];

        var self = this;
        this.root_scope.root.find('.t-member').each(function() {
            self.child_scopes.push(Scope.create_child(self.root_scope, $(this)));
        });

        // prepare scopes
        this.for_all_scopes(function() {

            var scope = this;
            self.prepare_navbar(scope);
            self.prepare_all_revs(scope);
            self.prepare_all_inl_revs(scope);
            self.prepare_sections_and_dscs(scope);

            if (scope.dcl_tables.length > 0) {
                var num_map = self.prepare_all_dcls(scope.dcl_tables.first());
                self.prepare_all_li(scope, num_map);
            }

        });

        this.is_prepared = true;
    };

    /** Utility function. Takes an jQuery object containing an array of
        elements that may or may not contain revision marker.
        Returns an a list of revisions for which a the node should be copied
        and for which revisions each of the copy would be shown. The result
        is an associative array: key identifies the revision to build the
        DOM for; the value is visibility map.
    */
    StandardRevisionPlugin.prototype.get_revision_map = function(lines) {
        var res = [];
        res[Rev.DIFF] = new VisibilityMap([Rev.DIFF]);

        var visible_by_line = [];

        // create separate elements when diff has rev marks
        var is_diff_clean = true;

        lines.each(function() {
            var rev_mark = $(this).find('.t-mark-rev').first();
            visible_by_line.push(get_visibility_map(rev_mark));
            if (rev_mark.length > 0) {
                is_diff_clean = false;
            }
        });

        // Track the lines shown in the previous revision. If the same lines
        // are shown in the current revision, simply display the element
        // of the previous revision, instead of creating a new one.
        var prev_rev = Rev.DIFF;
        var prev_visible = [];
        var i;

        if (is_diff_clean) {
            // in case the Rev.DIFF version does not contain rev marks, then
            // we can reuse the objects for other revisions. Rev.DIFF version
            // is fully visibily, so reflect that in the prev_visible array.
            for (i = 0; i < visible_by_line.length; i++) {
                prev_visible.push(i);
            }
        }

        for (var rev = Rev.FIRST; rev < Rev.LAST; ++rev) {
            res[rev] = new VisibilityMap();

            var curr_visible = [];
            for (i = 0; i < visible_by_line.length; i++) {
                if (visible_by_line[i].is_visible_on(rev)) {
                    curr_visible.push(i);
                }
            }

            if (curr_visible.length === 0) {
                continue;
            }

            // Maybe nothing has changed from the previous revision and we
            // can simply keep the node created for the previous revision
            if (array_equal(curr_visible, prev_visible)) {
                res[prev_rev].add(rev);
            } else {
                res[rev].add(rev);
                prev_visible = curr_visible;
                prev_rev = rev;
            }
        }

        return res;
    };

    /** Utility function. Takes a revision map as returned by
        get_revision_map and produces a visibility map from that.
    */
    StandardRevisionPlugin.prototype.revision_map_to_visibility = function(revs) {
        var visible = new VisibilityMap();
        for (var i = 0; i < revs.length; ++i) {
            visible.combine_or(revs[i]);
        }
        return visible;
    };

    /** Utility function. Deletes lines from multi-line links (such as these
        in dsc tables) that have marks nearby.
        Returns true if no lines are left. @a titles and @a marks must both
        refer to the children of .t-lines elements.
     */
    StandardRevisionPlugin.prototype.delete_lines = function(titles, marks, rev) {
        // Delete the lines
        var num_deleted = 0;
        var num_total = titles.length;

        marks.each(function(index) {
            var mark_span = $(this).children('.t-mark-rev');
            if (mark_span.length > 0) {
                var visible = get_visibility_map(mark_span.first());
                visible.add(Rev.DIFF);
                if (!visible.is_visible_on(rev)) {
                    titles.eq(index).remove();
                    $(this).remove();
                    num_deleted++;
                    return;
                }
            }
            mark_span.remove(); // delete marks in any case
        });

        // Delete this if empty
        return (num_deleted === num_total);
    };

    /** Creates the standard revision selection menu in the page and registers
        on_selection_change to be called whenever the seceltion changes.
    */
    StandardRevisionPlugin.prototype.create_selection_box = function() {
        var head_parent = $('#cpp-head-tools-right');

        this.select_div = $('<div/>').addClass('stdrev-select');

        var inner_div = $('<div/>').appendTo(this.select_div);
        var span = $('<span/>').addClass('stdrev-text')
                               .text('Standard revision: ')
                               .appendTo(inner_div);
        this.select = $('<select/>').appendTo(inner_div);

        for (var i = 0; i < desc.length; ++i) {
            $('<option/>').text(desc[i].title)
                          .attr('value', desc[i].rev.toString())
                          .appendTo(this.select);
        }

        this.select.one('mouseover', this.prepare.bind(this));
        this.select.change(this.on_selection_change.bind(this));
        this.select_div.prependTo(head_parent);
    };

    /** This function is called whenever the user changes the option selected
        in the selection box. The implementation hides the items that shouldn't
        be visible and reveals those that no longer need to be hidden (if any).
    */
    StandardRevisionPlugin.prototype.on_selection_change = function() {
        this.prepare();
        var rev = parseInt(this.select.val());
        this.tracker.to_rev(rev);

        // special treatment for rev boxes. Since these containers are very
        // simple, we can apply a CSS class to hide the border and rev markers
        // on non-diff revision.
        if (this.curr_rev === Rev.DIFF && rev !== Rev.DIFF) {
            this.for_all_scopes(function() {
                this.rev_tables.each(function() {
                    $(this).addClass('stdrev-rev-hide');
                });
            });
        }
        if (this.curr_rev !== Rev.DIFF && rev === Rev.DIFF) {
            this.for_all_scopes(function() {
                this.rev_tables.each(function() {
                    $(this).removeClass('stdrev-rev-hide');
                });
            });
        }

        this.curr_rev = rev;
    };

    var plugin = new StandardRevisionPlugin();
    plugin.create_selection_box();

});
