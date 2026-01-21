import cv2
import numpy as np
import argparse
import os
import sys


class Solution:
    def __init__(self):
        self.vehicles = {}  
        self.next_id = 0
import cv2
import numpy as np
import argparse
import os
import sys


class Solution:
    def __init__(self):
        self.vehicles = {}  
        self.next_id = 0

        
        self.max_lost = 10
        self.min_area = 600
        self.match_dist = 60
        self.min_age_to_count = 3  

    def forward(
        self,
        video_path: str,
        debug_output: str = None,
        min_area: int = None,
        match_dist: int = None,
        min_age_to_count: int = None,
        max_lost: int = None,
    ) -> int:
        if min_area is not None:
            self.min_area = min_area
        if match_dist is not None:
            self.match_dist = match_dist
        if min_age_to_count is not None:
            self.min_age_to_count = min_age_to_count
        if max_lost is not None:
            self.max_lost = max_lost

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0  

        backsub = cv2.createBackgroundSubtractorMOG2(
            history=700,
            varThreshold=40,
            detectShadows=False,
        )

        vehicle_count = 0
        frame_h = None
        roi_offset = None
        count_line = None
        writer = None
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        frame_h_full = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_h is None:
                frame_h = frame.shape[0]
                roi_offset = int(frame_h * 0.4)
                count_line = int(frame_h * 0.70)
              
                if debug_output:
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    writer = cv2.VideoWriter(debug_output, fourcc, fps, (frame.shape[1], frame.shape[0]))

            roi = frame[roi_offset:, :]
            fg = backsub.apply(roi)

            fg = cv2.medianBlur(fg, 5)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, kernel, iterations=2)
            fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)
            fg = cv2.dilate(fg, kernel, iterations=1)

            contours, _ = cv2.findContours(
                fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            detections = []
            for cnt in contours:
                if cv2.contourArea(cnt) < self.min_area:
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                cx = x + w // 2
                cy = y + h // 2 + roi_offset
                detections.append((cx, cy))

            updated_ids = set()

            for cx, cy in detections:
                best_id = None
                best_dist = self.match_dist

                for vid, (vx, vy, lost, counted, age) in self.vehicles.items():
                    dist = np.hypot(cx - vx, cy - vy)
                    if dist < best_dist and vid not in updated_ids:
                        best_dist = dist
                        best_id = vid

                if best_id is not None:
                    vx, vy, _, counted, age = self.vehicles[best_id]
                    age += 1

                    if (
                        not counted
                        and age >= self.min_age_to_count
                        and vy < count_line <= cy
                    ):
                        vehicle_count += 1
                        counted = True

                    self.vehicles[best_id] = (cx, cy, 0, counted, age)
                    updated_ids.add(best_id)

                else:
                    self.vehicles[self.next_id] = (cx, cy, 0, False, 1)
                    updated_ids.add(self.next_id)
                    self.next_id += 1

            for vid in list(self.vehicles.keys()):
                if vid not in updated_ids:
                    cx, cy, lost, counted, age = self.vehicles[vid]
                    lost += 1
                    if lost > self.max_lost:
                        del self.vehicles[vid]
                    else:
                        self.vehicles[vid] = (cx, cy, lost, counted, age)

           
            if debug_output and writer is not None:
                vis = frame.copy()
             
                cv2.line(vis, (0, roi_offset), (vis.shape[1], roi_offset), (255, 0, 0), 1)
                
                cv2.line(vis, (0, count_line), (vis.shape[1], count_line), (0, 0, 255), 2)

             
                for vid, (vx, vy, lost, counted, age) in self.vehicles.items():
                    color = (0, 255, 0) if not counted else (0, 128, 255)
                    cv2.circle(vis, (int(vx), int(vy)), 6, color, -1)
                    cv2.putText(vis, f"id:{vid} a:{age}", (int(vx) + 8, int(vy) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

                cv2.putText(vis, f"count:{vehicle_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                writer.write(vis)

        cap.release()
        if writer is not None:
            writer.release()
        return vehicle_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vehicle counter")
    parser.add_argument("video", nargs="?", help="Path to video file")
    args = parser.parse_args()

    if args.video:
       
        if not os.path.exists(args.video):
            print(0)
            sys.exit(0)

        sol = Solution()
        count = sol.forward(args.video)
        print(count)
        sys.exit(0)

   
    def run_streamlit():
        try:
            import streamlit as st
            import tempfile
        except Exception:
            sys.exit(1)

        st.title("Vehicle Counter")

        uploaded = st.file_uploader("Upload video file", type=["mp4", "avi", "mov", "mkv"])

        if uploaded is None:
            return

        suffix = os.path.splitext(uploaded.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

       
        if suffix.lower() == ".avi":
            try:
                conv_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                conv_tmp.close()

                cap = cv2.VideoCapture(tmp_path)
                if not cap.isOpened():
                    st.error("Unable to read uploaded video.")
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                    return

                fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

                if w == 0 or h == 0:
                    st.error("Uploaded video has invalid dimensions.")
                    cap.release()
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                    return

                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(conv_tmp.name, fourcc, fps, (w, h))

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)

                cap.release()
                out.release()
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                tmp_path = conv_tmp.name
            except Exception as e:
                st.error(f"Video conversion failed: {e}")
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                return

        st.video(tmp_path)

        with st.spinner("Processing video (this may take a while)..."):
            sol = Solution()
            count = sol.forward(tmp_path)

        st.success(str(count))

        try:
            os.remove(tmp_path)
        except Exception:
            pass

    run_streamlit()
