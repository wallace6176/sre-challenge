"""
Json alert parser and processor
"""
import json
from typing import List, Dict, Any
from collections import defaultdict
from dateutil import parser as dateparser

REQUIRED_KEYS = {"id", "timestamp", "service", "component", "severity", "metric", "value", "threshold", "description"}

def load_alerts_from_file(path: str) -> List[Dict[str, Any]]:
    """
    Open alerts JSON file and ensure the top level 'alerts' list is present
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if "alerts" not in data:
        raise ValueError("Invalid file format: missing top-level 'alerts' list.")
    return data["alerts"]

def validate_alert(alert: Dict[str, Any]) -> bool:
    """
    Validate an alert against the required keys
    """
    return REQUIRED_KEYS.issubset(alert.keys())

def filter_alerts(alerts: List[Dict[str, Any]],
                  severity: str = None,
                  service: str = None,
                  start_time: str = None,
                  end_time: str = None) -> List[Dict[str, Any]]:
    """
    Filter alerts by severity, service and time range
    """
    filtered = []
    for alert in alerts:
        if not validate_alert(alert):
            print(f"Invalid structure for alert {alert['id']}")
            continue

        if severity and alert["severity"].lower() != severity.lower():
            continue
        if service and alert["service"] != service:
            continue

        alert_time = dateparser.parse(alert["timestamp"])
        if start_time and alert_time < dateparser.parse(start_time):
            continue
        if end_time and alert_time > dateparser.parse(end_time):
            continue

        filtered.append(alert)

    return filtered

def dedup_alerts_by_id(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate alerts by alert ID
    """
    latest_alerts = {}
    for alert in alerts:
        alert_id = alert.get("id")
        timestamp = dateparser.parse(alert["timestamp"])

        if alert_id in latest_alerts:
            existing_timestamp = dateparser.parse(latest_alerts[alert_id]["timestamp"])
            if timestamp > existing_timestamp:
                latest_alerts[alert_id] = alert
        else:
            latest_alerts[alert_id] = alert

    return list(latest_alerts.values())

def group_alerts_by_component(alerts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group related alerts (alerts from the same component)
    """
    groups = defaultdict(list)
    for alert in alerts:
        groups[alert["component"]].append(alert)
    return groups

def calculate_priority_score(alert: Dict[str, Any],
                  component_count: int = 1) -> float:
    """
    Calculate alert priority based on severity,
    deviation from threshold and number of affected components
    """
    severity_weights = {
        "critical": 10,
        "warning": 5,
        "info": 1
    }


    severity = alert['severity']
    value = alert['value']
    threshold = alert['threshold']

    if (severity not in severity_weights
            or not isinstance(value, (int, float))
            or not isinstance(threshold, (int,float))
            or threshold == 0):
        raise ValueError(f"Invalid key values: {alert}")

    severity_score = severity_weights[severity]
    deviation_pct = max(0.0, (value - threshold) / threshold)
    component_factor = 1 + (component_count - 1) * 0.1
    score = severity_score * (1 + deviation_pct) * component_factor
    return round(score, 2)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse and process alerts in a JSON file.")
    parser.add_argument("file", help="Path to the JSON file")
    parser.add_argument("--severity", help="Filter by severity level (e.g., critical)")
    parser.add_argument("--service", help="Filter by affected service")
    parser.add_argument("--start", help="Filter by time range: start time (example: 2025-06-06T00:00:00Z)")
    parser.add_argument("--end", help="Filter by time range: end time (example: 2025-06-06T00:00:00Z)")
    args = parser.parse_args()

    try:
        alerts = load_alerts_from_file(args.file)
        filtered_alerts = filter_alerts(alerts, args.severity, args.service, args.start, args.end)
        deduped_alerts = dedup_alerts_by_id(filtered_alerts)
        grouped = group_alerts_by_component(deduped_alerts)

        for component, alerts in grouped.items():
            print(f"\nComponent: {component}")
            for alert in alerts:
                priority_score = calculate_priority_score(alert)
                print(f"  - {alert['id']} | {alert['severity']} | {alert['timestamp']} | {alert['description']} | priority: {priority_score}")
    except Exception as e:
        print(f"Error: {e}")
