import argparse
import csv
import json
import math
from dataclasses import dataclass
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


Point = Tuple[float, float]


@dataclass
class MovementPoint:
    time: float
    x: float
    y: float


@dataclass
class CompensationSample:
    wrist_y: float
    shoulder_y: Optional[float] = None
    hip_y: Optional[float] = None


def read_movement_csv(path: str) -> List[MovementPoint]:
    points: List[MovementPoint] = []

    with open(path, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                points.append(
                    MovementPoint(
                        time=float(row["Time"]),
                        x=float(row["Wrist_X"]),
                        y=float(row["Wrist_Y"]),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue

    return points


def read_angle_csv(path: str) -> Dict[str, List[float]]:
    angle_columns: Dict[str, List[float]] = {}

    with open(path, "r", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            return angle_columns

        for name in reader.fieldnames:
            if name != "Time":
                angle_columns[name] = []

        for row in reader:
            for name in angle_columns:
                try:
                    angle_columns[name].append(float(row[name]))
                except (KeyError, TypeError, ValueError):
                    continue

    return angle_columns


def read_reference_path_csv(path: str) -> List[Point]:
    points: List[Point] = []

    with open(path, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            point = _read_xy_from_row(row)
            if point is not None:
                points.append(point)

    return points


def read_unity_session_json(path: str) -> Tuple[List[MovementPoint], Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    samples = data.get("playerHandSamples", [])
    movement_points: List[MovementPoint] = []

    for sample in samples:
        try:
            position = sample["position"]
            movement_points.append(
                MovementPoint(
                    time=float(sample["timeSeconds"]),
                    x=float(position["x"]),
                    # Unity PlayerHand moves across the X/Z floor plane.
                    y=float(position["z"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue

    return movement_points, data


def summarize_unity_session_json(
    data: Dict[str, object],
    movement_points: Sequence[MovementPoint],
) -> str:
    samples = data.get("playerHandSamples", [])
    target_events = data.get("targetEvents", [])
    first_sample = samples[0] if samples else None
    has_xyz = False

    if isinstance(first_sample, dict):
        position = first_sample.get("position")
        has_xyz = (
            isinstance(position, dict) and
            all(axis in position for axis in ("x", "y", "z"))
        )

    lines = [
        "Unity Session JSON",
        "------------------",
        f"Game: {data.get('gameName', 'Not available')}",
        f"Difficulty: {data.get('selectedDifficulty', 'Not available')}",
        f"Targets: {data.get('targetsCollected', 0)} / {data.get('totalTargets', 0)}",
        f"Target Events: {len(target_events)}",
        f"PlayerHand Samples: {len(samples)}",
        f"Movement Points Extracted: {len(movement_points)}",
        f"XYZ Positions Present: {'Yes' if has_xyz else 'No'}",
    ]

    if movement_points:
        lines.append(
            "First Sample: "
            f"t={movement_points[0].time:.4f}, "
            f"x={movement_points[0].x:.4f}, "
            f"z={movement_points[0].y:.4f}"
        )

    return "\n".join(lines)


def _read_xy_from_row(row: Dict[str, str]) -> Optional[Point]:
    possible_columns = (
        ("X", "Y"),
        ("x", "y"),
        ("Wrist_X", "Wrist_Y"),
        ("Target_X", "Target_Y"),
    )

    for x_name, y_name in possible_columns:
        if x_name in row and y_name in row:
            try:
                return float(row[x_name]), float(row[y_name])
            except (TypeError, ValueError):
                return None

    return None


def analyze_movement(
    movement_points: Sequence[MovementPoint],
    angle_series: Optional[Dict[str, List[float]]] = None,
    reference_path: Optional[Sequence[Point]] = None,
    target: Optional[Point] = None,
    compensation_samples: Optional[Sequence[CompensationSample]] = None,
    accuracy_radius: float = 1.0,
) -> Dict[str, object]:
    clean_points = sorted(
        movement_points,
        key=lambda point: point.time,
    )

    path = [(point.x, point.y) for point in clean_points]
    times = [point.time for point in clean_points]
    segment_distances, segment_speeds, speed_times = _segment_motion(
        clean_points
    )

    total_distance = sum(segment_distances)
    duration = _duration(times)
    accelerations = _accelerations(segment_speeds, speed_times)

    report = {
        "sample_count": len(clean_points),
        "duration": duration,
        "trajectory": {
            "point_count": len(path),
            "total_distance": total_distance,
            "deviation": trajectory_deviation(path, reference_path),
        },
        "speed": {
            "average": mean(segment_speeds) if segment_speeds else 0.0,
            "maximum": max(segment_speeds) if segment_speeds else 0.0,
        },
        # Paper-aligned smoothness: variance of the acceleration profile.
        # Lower values indicate smoother movement in this prototype metric.
        "smoothness": {
            "acceleration_variance": variance(accelerations),
            "acceleration_sample_count": len(accelerations),
        },
        "accuracy": positional_accuracy(path, target, accuracy_radius),
        "joint_angles": joint_angle_variation(angle_series or {}),
        "rom": range_of_motion(angle_series or {}),
        "wrist_position_rom": wrist_position_rom(path),
        "compensation": compensation_ratio(compensation_samples or []),
    }

    return report


def _segment_motion(
    points: Sequence[MovementPoint],
) -> Tuple[List[float], List[float], List[float]]:
    distances: List[float] = []
    speeds: List[float] = []
    speed_times: List[float] = []

    for previous, current in zip(points, points[1:]):
        dt = current.time - previous.time
        distance = math.dist((previous.x, previous.y), (current.x, current.y))
        distances.append(distance)

        if dt > 0:
            speeds.append(distance / dt)
            speed_times.append(previous.time + (dt / 2.0))

    return distances, speeds, speed_times


def _accelerations(
    speeds: Sequence[float],
    speed_times: Sequence[float],
) -> List[float]:
    accelerations: List[float] = []

    for index in range(1, len(speeds)):
        dt = speed_times[index] - speed_times[index - 1]
        if dt > 0:
            accelerations.append((speeds[index] - speeds[index - 1]) / dt)

    return accelerations


def _duration(times: Sequence[float]) -> float:
    if not times:
        return 0.0

    return max(times) - min(times)


def variance(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None

    average = mean(values)
    return sum((value - average) ** 2 for value in values) / len(values)


def joint_angle_variation(
    angle_series: Dict[str, List[float]]
) -> Dict[str, Dict[str, Optional[float]]]:
    results: Dict[str, Dict[str, Optional[float]]] = {}

    for name, values in angle_series.items():
        clean_values = [value for value in values if math.isfinite(value)]

        if not clean_values:
            results[name] = {
                "minimum": None,
                "maximum": None,
                "mean": None,
                "average_absolute_change": None,
            }
            continue

        changes = [
            abs(current - previous)
            for previous, current in zip(clean_values, clean_values[1:])
        ]

        results[name] = {
            "minimum": min(clean_values),
            "maximum": max(clean_values),
            "mean": mean(clean_values),
            "average_absolute_change": mean(changes) if changes else 0.0,
        }

    return results


def range_of_motion(
    angle_series: Dict[str, List[float]]
) -> Dict[str, Optional[float]]:
    rom: Dict[str, Optional[float]] = {}

    for name, values in angle_series.items():
        clean_values = [value for value in values if math.isfinite(value)]
        rom[name] = (
            max(clean_values) - min(clean_values)
            if clean_values
            else None
        )

    return rom


def wrist_position_rom(path: Sequence[Point]) -> Dict[str, Optional[float]]:
    if not path:
        return {
            "x": None,
            "y": None,
        }

    x_values = [point[0] for point in path]
    y_values = [point[1] for point in path]

    return {
        "x": max(x_values) - min(x_values),
        "y": max(y_values) - min(y_values),
    }


def trajectory_deviation(
    path: Sequence[Point],
    reference_path: Optional[Sequence[Point]],
) -> Optional[float]:
    if not path or not reference_path:
        return None

    sample_count = min(len(path), len(reference_path))
    if sample_count == 0:
        return None

    sampled_path = resample_path(path, sample_count)
    sampled_reference = resample_path(reference_path, sample_count)
    deviations = [
        math.dist(actual, reference)
        for actual, reference in zip(sampled_path, sampled_reference)
    ]

    return mean(deviations) if deviations else None


def resample_path(
    path: Sequence[Point],
    sample_count: int,
) -> List[Point]:
    if sample_count <= 0 or not path:
        return []

    if len(path) == 1 or sample_count == 1:
        return [path[0]] * sample_count

    sampled: List[Point] = []
    last_index = len(path) - 1

    for index in range(sample_count):
        position = index * last_index / (sample_count - 1)
        left_index = int(math.floor(position))
        right_index = min(left_index + 1, last_index)
        blend = position - left_index

        left = path[left_index]
        right = path[right_index]
        sampled.append(
            (
                left[0] + (right[0] - left[0]) * blend,
                left[1] + (right[1] - left[1]) * blend,
            )
        )

    return sampled


def positional_accuracy(
    path: Sequence[Point],
    target: Optional[Point],
    accuracy_radius: float,
) -> Dict[str, Optional[float]]:
    if not path or target is None:
        return {
            "final_distance": None,
            "score_percent": None,
        }

    radius = max(accuracy_radius, 1e-9)
    final_distance = math.dist(path[-1], target)

    return {
        "final_distance": final_distance,
        "score_percent": max(0.0, 100.0 * (1.0 - final_distance / radius)),
    }


def compensation_ratio(
    samples: Sequence[CompensationSample],
) -> Dict[str, Optional[float]]:
    if not samples:
        return {
            "trunk_movement": None,
            "wrist_movement": None,
            "ratio": None,
            "status": "Not available",
        }

    wrist_values = [
        sample.wrist_y
        for sample in samples
        if math.isfinite(sample.wrist_y)
    ]
    trunk_values = []

    for sample in samples:
        values = [
            value
            for value in (sample.shoulder_y, sample.hip_y)
            if value is not None and math.isfinite(value)
        ]
        if values:
            trunk_values.append(mean(values))

    if not wrist_values or not trunk_values:
        return {
            "trunk_movement": None,
            "wrist_movement": None,
            "ratio": None,
            "status": "Not available",
        }

    wrist_movement = max(wrist_values) - min(wrist_values)
    trunk_movement = max(trunk_values) - min(trunk_values)

    if wrist_movement <= 0:
        ratio = None
        status = "No wrist movement detected"
    else:
        ratio = trunk_movement / wrist_movement
        status = "Ratio computed; no clinical threshold applied"

    return {
        "trunk_movement": trunk_movement,
        "wrist_movement": wrist_movement,
        "ratio": ratio,
        "status": status,
    }


def format_report(report: Dict[str, object]) -> str:
    trajectory = report["trajectory"]
    speed = report["speed"]
    smoothness = report["smoothness"]
    accuracy = report["accuracy"]
    compensation = report["compensation"]

    lines = [
        "========================================",
        "RehabQuest Movement Analysis",
        "========================================",
        f"Samples: {report['sample_count']}",
        f"Duration: {_format_number(report['duration'], ' seconds')}",
        f"Total Movement Distance: {_format_number(trajectory['total_distance'])}",
        f"Average Speed: {_format_number(speed['average'])}",
        f"Maximum Speed: {_format_number(speed['maximum'])}",
        (
            "Trajectory Deviation: "
            f"{_format_number(trajectory['deviation'])}"
        ),
        (
            "Smoothness Acceleration Variance: "
            f"{_format_number(smoothness['acceleration_variance'])}"
        ),
        (
            "Accuracy: "
            f"{_format_number(accuracy['score_percent'], '%')}"
        ),
        (
            "Accuracy Final Distance: "
            f"{_format_number(accuracy['final_distance'])}"
        ),
        (
            "Compensation Ratio: "
            f"{_format_number(compensation['ratio'])}"
        ),
        f"Compensation Status: {compensation['status']}",
        "",
        "Joint-Angle Variation",
    ]

    joint_angles = report["joint_angles"]
    if joint_angles:
        for name, values in joint_angles.items():
            lines.append(
                f"- {name}: min {_format_number(values['minimum'])}, "
                f"max {_format_number(values['maximum'])}, "
                f"mean {_format_number(values['mean'])}, "
                "average absolute change "
                f"{_format_number(values['average_absolute_change'])}"
            )
    else:
        lines.append("- Not available")

    lines.append("")
    lines.append("ROM = maximum joint angle - minimum joint angle")

    rom = report["rom"]
    if rom:
        for name, value in rom.items():
            lines.append(f"- {name}: {_format_number(value, ' degrees')}")
    else:
        lines.append("- Not available")

    wrist_rom = report["wrist_position_rom"]
    lines.extend(
        [
            "",
            "Wrist Position Range",
            f"- X: {_format_number(wrist_rom['x'])}",
            f"- Y: {_format_number(wrist_rom['y'])}",
        ]
    )

    return "\n".join(lines)


def _format_number(
    value: Optional[float],
    suffix: str = "",
) -> str:
    if value is None:
        return "Not available"

    return f"{value:.4f}{suffix}"


def sample_analysis() -> Dict[str, object]:
    movement = [
        MovementPoint(0.0, 0.20, 0.80),
        MovementPoint(0.5, 0.30, 0.70),
        MovementPoint(1.0, 0.42, 0.58),
        MovementPoint(1.5, 0.55, 0.45),
        MovementPoint(2.0, 0.68, 0.34),
        MovementPoint(2.5, 0.78, 0.28),
    ]

    reference_path = [
        (0.20, 0.80),
        (0.32, 0.68),
        (0.44, 0.56),
        (0.56, 0.44),
        (0.68, 0.32),
        (0.80, 0.25),
    ]

    angle_series = {
        "Right_Elbow_Angle": [150.0, 142.0, 132.0, 120.0, 115.0, 118.0],
        "Right_Shoulder_Angle": [35.0, 41.0, 48.0, 55.0, 58.0, 56.0],
    }

    compensation_samples = [
        CompensationSample(0.80, shoulder_y=0.35, hip_y=0.62),
        CompensationSample(0.70, shoulder_y=0.36, hip_y=0.62),
        CompensationSample(0.58, shoulder_y=0.36, hip_y=0.63),
        CompensationSample(0.45, shoulder_y=0.37, hip_y=0.63),
        CompensationSample(0.34, shoulder_y=0.37, hip_y=0.64),
        CompensationSample(0.28, shoulder_y=0.38, hip_y=0.64),
    ]

    return analyze_movement(
        movement,
        angle_series=angle_series,
        reference_path=reference_path,
        target=(0.80, 0.25),
        compensation_samples=compensation_samples,
    )


def no_movement_sample_analysis() -> Dict[str, object]:
    movement = [
        MovementPoint(0.0, 0.50, 0.50),
        MovementPoint(0.5, 0.50, 0.50),
        MovementPoint(1.0, 0.50, 0.50),
    ]

    return analyze_movement(
        movement,
        angle_series={"Right_Elbow_Angle": [120.0, 120.0, 120.0]},
        target=(0.50, 0.50),
        compensation_samples=[
            CompensationSample(0.50, shoulder_y=0.40, hip_y=0.70),
            CompensationSample(0.50, shoulder_y=0.40, hip_y=0.70),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the unified RehabQuest movement analyzer."
    )
    parser.add_argument(
        "--movement-csv",
        default="hand_movement.csv",
        help="CSV containing Time, Wrist_X, and Wrist_Y columns.",
    )
    parser.add_argument(
        "--unity-session-json",
        help=(
            "JSON exported by Unity Reach & Collect. "
            "PlayerHand x/z samples are analyzed as the movement plane."
        ),
    )
    parser.add_argument(
        "--angle-csv",
        action="append",
        default=[],
        help="CSV containing Time plus one or more joint-angle columns.",
    )
    parser.add_argument(
        "--reference-csv",
        help="Optional CSV containing X,Y or Wrist_X,Wrist_Y reference path.",
    )
    parser.add_argument("--target-x", type=float)
    parser.add_argument("--target-y", type=float)
    parser.add_argument(
        "--accuracy-radius",
        type=float,
        default=1.0,
        help="Prototype normalized distance used to convert target error to percent.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Run a controlled sample analysis instead of reading CSV files.",
    )
    parser.add_argument(
        "--no-movement-sample",
        action="store_true",
        help="Run a controlled no-movement safety check.",
    )

    args = parser.parse_args()

    if args.sample:
        report = sample_analysis()
    elif args.no_movement_sample:
        report = no_movement_sample_analysis()
    else:
        unity_summary = None

        if args.unity_session_json:
            movement, unity_data = read_unity_session_json(
                args.unity_session_json
            )
            unity_summary = summarize_unity_session_json(
                unity_data,
                movement
            )
        else:
            movement = read_movement_csv(args.movement_csv)

        angle_series: Dict[str, List[float]] = {}

        for angle_csv in args.angle_csv:
            angle_series.update(read_angle_csv(angle_csv))

        reference_path = (
            read_reference_path_csv(args.reference_csv)
            if args.reference_csv
            else None
        )
        target = (
            (args.target_x, args.target_y)
            if args.target_x is not None and args.target_y is not None
            else None
        )

        report = analyze_movement(
            movement,
            angle_series=angle_series,
            reference_path=reference_path,
            target=target,
            accuracy_radius=args.accuracy_radius,
        )

        if unity_summary is not None:
            print(unity_summary)
            print()

    print(format_report(report))


if __name__ == "__main__":
    main()
