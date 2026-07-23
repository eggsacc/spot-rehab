import numpy as np, open3d as o3d
import sys, os

def render(pcd, bg_color):
	pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.load(pcd)))
	vis = o3d.visualization.Visualizer()
	vis.create_window(visible=True)
	vis.get_render_option().background_color = bg_color
	vis.add_geometry(pc)
	vis.run()
	
if __name__ == "__main__":
	pcd = os.path.join(sys.argv[1], "merged_points.npy") if len(sys.argv) > 1 else None
	if not pcd:
		print("Specify autowalk cache parent directory!")
		sys.exit()
		
	bg_color = [0, 0, 0]
	if len(sys.argv) > 2:
		for i in range(3):
			bg_color[i] = sys.argv[i + 2]
	render(pcd,bg_color)
	
		
			


