from typing import Dict, Any, List, Optional

class VoiceTurnTakingEndpointingDetector:
    """
    Evaluates real-time audio frame energy levels, speech confidence, and silence duration
    to arbitrate conversational turn transitions and barge-in interruptions.
    """
    def __init__(
        self,
        min_silence_duration_ms: int = 450,
        barge_in_energy_threshold_db: float = -28.0,
        consecutive_speech_frames_threshold: int = 3
    ):
        self.min_silence_duration_ms = min_silence_duration_ms
        self.barge_in_energy_threshold_db = barge_in_energy_threshold_db
        self.consecutive_speech_frames_threshold = consecutive_speech_frames_threshold

    def evaluate_audio_frame_stream(
        self,
        frames: List[Dict[str, Any]],
        agent_is_speaking: bool = False
    ) -> Dict[str, Any]:
        consecutive_speech = 0
        consecutive_silence_ms = 0
        user_interrupted = False
        turn_completed = False
        speech_started = False
        frame_audit = []

        for frame in frames:
            energy_db = frame.get("energy_db", -60.0)
            duration_ms = frame.get("duration_ms", 20)
            is_speech = energy_db >= self.barge_in_energy_threshold_db

            if is_speech:
                consecutive_speech += 1
                consecutive_silence_ms = 0
                if consecutive_speech >= self.consecutive_speech_frames_threshold:
                    speech_started = True
                    if agent_is_speaking:
                        user_interrupted = True
            else:
                consecutive_speech = 0
                if speech_started:
                    consecutive_silence_ms += duration_ms
                    if consecutive_silence_ms >= self.min_silence_duration_ms:
                        turn_completed = True

            frame_audit.append({
                "energy_db": energy_db,
                "is_speech": is_speech,
                "silence_accumulated_ms": consecutive_silence_ms,
                "interrupted": user_interrupted,
                "turn_completed": turn_completed
            })

        decision = "CONTINUE_LISTENING"
        if user_interrupted:
            decision = "TRIGGER_BARGE_IN_INTERRUPT"
        elif turn_completed:
            decision = "DISPATCH_AGENT_SYNTHESIS"

        return {
            "decision": decision,
            "barge_in_detected": user_interrupted,
            "turn_completed": turn_completed,
            "final_silence_ms": consecutive_silence_ms,
            "analyzed_frames_count": len(frames),
            "frame_audit": frame_audit
        }
