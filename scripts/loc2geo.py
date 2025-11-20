from my_pkg.tools import parse_keyframe_file

def loc2geo(keyframeid_path, locfile_path, outputgeo_path):
    keyframe_mapping = parse_keyframe_file(keyframeid_path)

    loc_dict = {}
    i = 0

    with open(locfile_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 8:
                continue
            filename = parts[0]
            try:
                # 这里减1，确保uav/001.jpg 对应 frame_id=0
                frame_id = i
                i+=1
            except:
                continue

            col6 = parts[5]
            col7 = parts[6]
            loc_dict[frame_id] = (col6, col7)

    missing_count = 0
    with open(outputgeo_path, "w") as fout:
        for keyframe_id, frame_id in keyframe_mapping.items():
            if frame_id in loc_dict:
                col6, col7 = loc_dict[frame_id]
                fout.write(f"{col6} {col7}\n")
            else:
                print(f"Warning: frame_id {frame_id} not found in loc file")
                missing_count += 1

    print(f"Total keyframes: {len(keyframe_mapping)}")
    print(f"Found matches: {len(keyframe_mapping) - missing_count}")
    print(f"Missing matches: {missing_count}")

# 调用示例
# loc2geo("keyframeid.txt", "loc.txt", "output_geo.txt")

if __name__ == '__main__':
    keyframeid_path = "/home/lty/outputs/seu0524/009/KeyFrameId.txt"
    # keyframeid_path = "/home/lty/outputs/seu0524/005/KeyFrameId.txt"
    locfile_path = "/home/lty/outputs/seu0524/009/loc_elevpnp.txt"
    outputgeo_path = "/home/lty/paper/results/052409/elevpnp.txt"
    loc2geo(keyframeid_path, locfile_path, outputgeo_path)