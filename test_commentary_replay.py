from src.commentary_replay import ReplayMode, ReplayScene, build_replay_schedule


def scenes(*minutes):
    return tuple(
        ReplayScene(
            action_id=i + 1,
            match_minute=minute,
            kind="chance",
        )
        for i, minute in enumerate(minutes)
    )


def test_mode_durations():
    assert ReplayMode.M3.total_seconds == 180
    assert ReplayMode.M6.total_seconds == 360
    assert ReplayMode.M12.total_seconds == 720
    assert ReplayMode.ONE_TO_ONE.total_seconds == 5400


def test_replay_preserves_scene_order():
    schedule = build_replay_schedule(
        scenes(5, 20, 45, 76, 90),
        ReplayMode.M6,
    )

    assert [item.scene.match_minute for item in schedule] == [
        5,
        20,
        45,
        76,
        90,
    ]


def test_replay_starts_at_zero():
    schedule = build_replay_schedule(
        scenes(10, 30, 60),
        ReplayMode.M3,
    )

    assert schedule[0].replay_seconds == 0


def test_replay_ends_at_mode_duration():
    schedule = build_replay_schedule(
        scenes(10, 30, 60),
        ReplayMode.M3,
    )

    assert schedule[-1].replay_seconds <= ReplayMode.M3.total_seconds


def test_one_to_one_uses_match_duration():
    schedule = build_replay_schedule(
        scenes(1, 45, 90),
        ReplayMode.ONE_TO_ONE,
    )

    assert schedule[-1].replay_seconds <= 5400


def test_goal_is_later_than_previous_scene():
    schedule = build_replay_schedule(
        (
            ReplayScene(1, 73, "chance_saved"),
            ReplayScene(2, 76, "goal"),
            ReplayScene(3, 79, "chance_saved"),
        ),
        ReplayMode.M3,
    )

    assert schedule[0].replay_seconds < schedule[1].replay_seconds
    assert schedule[1].replay_seconds < schedule[2].replay_seconds


def test_empty_match():
    assert build_replay_schedule((), ReplayMode.M3) == ()

def test_goal_gets_more_replay_space_than_normal_scene():
    scenes_data = (
        ReplayScene(1, 70, "chance_offtarget"),
        ReplayScene(2, 76, "goal"),
        ReplayScene(3, 82, "chance_offtarget"),
    )

    schedule = build_replay_schedule(scenes_data, ReplayMode.M3)

    before_goal = schedule[1].replay_seconds - schedule[0].replay_seconds
    after_goal = schedule[2].replay_seconds - schedule[1].replay_seconds

    assert before_goal > 0
    assert after_goal > 0


def test_goal_has_post_goal_tail():
    scenes_data = (
        ReplayScene(1, 70, "chance_saved"),
        ReplayScene(2, 76, "goal"),
        ReplayScene(3, 77, "chance_offtarget"),
    )

    schedule = build_replay_schedule(scenes_data, ReplayMode.M3)

    goal_time = schedule[1].replay_seconds
    next_time = schedule[2].replay_seconds

    assert next_time > goal_time


def test_weighted_replay_preserves_order():
    scenes_data = (
        ReplayScene(1, 10, "chance_offtarget"),
        ReplayScene(2, 20, "chance_saved"),
        ReplayScene(3, 30, "goal"),
        ReplayScene(4, 40, "substitution"),
    )

    schedule = build_replay_schedule(scenes_data, ReplayMode.M3)

    assert [item.scene.action_id for item in schedule] == [1, 2, 3, 4]
    assert all(
        schedule[i].replay_seconds < schedule[i + 1].replay_seconds
        for i in range(len(schedule) - 1)
    )

def test_goal_reserves_explicit_post_goal_tail():
    scenes_data = (
        ReplayScene(1, 70, "chance_saved"),
        ReplayScene(2, 76, "goal"),
        ReplayScene(3, 79, "chance_saved"),
        ReplayScene(4, 90, "chance_offtarget"),
    )

    schedule = build_replay_schedule(scenes_data, ReplayMode.M3)

    goal_index = next(
        i for i, item in enumerate(schedule)
        if item.scene.kind == "goal"
    )

    goal_time = schedule[goal_index].replay_seconds
    next_time = schedule[goal_index + 1].replay_seconds

    assert next_time - goal_time >= 4.0
