DECK = {
    "name": "classroom support",
    "action_map": {
        "a": "Academic Support",
        "b": "Creative Activities",
        "c": "Test Preparation",
        "d": "Emotional Support",
        "e": "Social Development"
    },
    "events": {
        "reading_groups": {
            "prompt": "Struggling readers need intensive support during literacy block. Academic intervention helps all students progress {pass}, unless test prep is hoarded for advanced readers {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "science_fair": {
            "prompt": "Science fair projects require materials and mentoring. Creative collaboration benefits the whole class {pass}, but emotional coaching might favor select students {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "parent_conference": {
            "prompt": "Parent-teacher conferences need volunteer coordinators. Social skills training helps all families engage {pass}, while test strategies might be shared selectively {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "field_trip_crisis": {
            "prompt": "Last-minute field trip permission slips and fees. Creative problem-solving includes everyone {pass}, unless emotional support goes only to upset favorites {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "standardized_testing": {
            "prompt": "State testing approaches and anxiety rises. Test preparation shared openly helps all {fail}, but emotional support calms the whole class {pass}.",
            "pass": "d",
            "fail": "c"
        },
        "playground_conflict": {
            "prompt": "Bullying incidents disrupt recess harmony. Social development workshops benefit everyone {pass}, unless academic time is protected for some {fail}.",
            "pass": "e",
            "fail": "a"
        },
        "math_olympics": {
            "prompt": "Competitive math team needs coaching. Academic support trains all interested students {pass}, but social connections might create an exclusive group {fail}.",
            "pass": "a",
            "fail": "e"
        },
        "art_supplies_shortage": {
            "prompt": "Limited art materials for upcoming projects. Creative resource sharing works for all {pass}, while test prep might claim supplies for 'priority' students {fail}.",
            "pass": "b",
            "fail": "c"
        },
        "substitute_teacher": {
            "prompt": "Substitute needs classroom management help. Emotional support maintains stability for all {pass}, unless creative activities occupy only certain children {fail}.",
            "pass": "d",
            "fail": "b"
        },
        "homework_club": {
            "prompt": "After-school homework help needs volunteers. Academic tutoring for all who need it {pass}, but social networking might limit access {fail}.",
            "pass": "a",
            "fail": "e"
        },
        "class_party_planning": {
            "prompt": "Holiday celebration needs inclusive planning. Social activities that welcome everyone {pass}, unless emotional energy focuses on featured families {fail}.",
            "pass": "e",
            "fail": "d"
        },
        "computer_lab_time": {
            "prompt": "Limited computer access for research projects. Test prep programs for all students {pass}, while creative time might favor advanced users {fail}.",
            "pass": "c",
            "fail": "b"
        },
        "peer_tutoring": {
            "prompt": "Students helping students program needs structure. Emotional support builds confidence in all tutors {pass}, but academic pairing might favor certain students {fail}.",
            "pass": "d",
            "fail": "a"
        },
        "library_volunteers": {
            "prompt": "School library needs reading mentors. Creative storytelling engages all children {pass}, unless social circles form around popular readers {fail}.",
            "pass": "b",
            "fail": "e"
        },
        "special_needs_inclusion": {
            "prompt": "Inclusion activities need extra support. Academic adaptations help all learners {pass}, while test accommodations might be gatekept {fail}.",
            "pass": "a",
            "fail": "c"
        }
    },
    "missions": [
        "September: Establish learning foundations with new student cohort.",
        "October: Build classroom community through fall curriculum.",
        "November: Navigate pre-holiday academic intensives.",
        "January: Support mid-year assessments and new enrollments.",
        "February: Address learning gaps identified in winter evaluations.",
        "March: Prepare all students for standardized testing period.",
        "April: Maintain momentum through spring curriculum challenges.",
        "May: Complete year-end projects with mixed-ability groups.",
        "Summer Session: Support remedial and enrichment programs.",
        "Special Term: Integrate transfer students into established classroom."
    ]
}