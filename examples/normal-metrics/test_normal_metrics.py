import math,unittest
from normal_metrics import angular_degrees,compare_normals
class NormalMetricsTests(unittest.TestCase):
 def test_axes_and_antiparallel(self):
  self.assertEqual(angular_degrees((0,0,1),(0,0,2)),0)
  self.assertEqual(angular_degrees((0,0,1),(0,0,-1)),180)
  self.assertAlmostEqual(angular_degrees((1,0,0),(0,1,0)),90)
 def test_tiny_angle_and_joint_bounds(self):
  theta=math.radians(.0045);actual=(math.sin(theta),0,math.cos(theta))
  self.assertAlmostEqual(angular_degrees((0,0,1),actual),.0045,places=10)
  r=compare_normals([(0,0,1)],[actual],[(0,0,1)],component_limit=1e-4,angle_limit_degrees=.01,unit_error_limit=1e-6,geometric_angle_limit_degrees=.01)
  self.assertTrue(r['passed'])
  self.assertFalse(compare_normals([(0,0,1)],[actual],angle_limit_degrees=.001)['passed'])
 def test_component_and_unit_checks_are_independent(self):
  r=compare_normals([(0,0,1)],[(0,0,1.01)],angle_limit_degrees=.01,unit_error_limit=1e-6)
  self.assertEqual(r['maxima']['angleDegrees'],0);self.assertFalse(r['passed'])
  self.assertFalse(compare_normals([(0,0,1)],[(0,0,-1)],[(0,0,1)],geometric_angle_limit_degrees=.01)['passed'])
 def test_invalid_inputs_and_no_universal_default(self):
  self.assertIsNone(compare_normals([(0,0,1)],[(0,0,1)])['passed'])
  for bad in [(0,0,0),(0,float('nan'),1),(1,2)]:
   with self.assertRaises(ValueError):angular_degrees((0,0,1),bad)
  with self.assertRaises(ValueError):compare_normals([(0,0,1)],[])
  with self.assertRaises(ValueError):compare_normals([(0,0,1)],[(0,0,1)],geometric_angle_limit_degrees=1)
if __name__=='__main__':unittest.main()
