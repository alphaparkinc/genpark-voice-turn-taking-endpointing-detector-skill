import json
from client import VoiceTurnTakingEndpointingDetector

def main():
    detector = VoiceTurnTakingEndpointingDetector(min_silence_duration_ms=400)
    # Simulate user uttering words followed by silence
    frames = [
        {"energy_db": -22.0, "duration_ms": 100},
        {"energy_db": -20.0, "duration_ms": 100},
        {"energy_db": -24.0, "duration_ms": 100},
        {"energy_db": -55.0, "duration_ms": 200},
        {"energy_db": -60.0, "duration_ms": 250}
    ]
    result = detector.evaluate_audio_frame_stream(frames, agent_is_speaking=False)
    print("Voice Turn-Taking Result:")
    print(json.dumps(result, indent=2))
    assert result["turn_completed"] is True
    assert result["decision"] == "DISPATCH_AGENT_SYNTHESIS"
    print("Voice turn-taking detector verification: PASS")

if __name__ == "__main__":
    main()
