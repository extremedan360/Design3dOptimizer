"""Original stdlib normal comparison helpers. Thresholds are supplied by the caller."""
import math

def vector(value):
 values=tuple(float(x) for x in value)
 if len(values)!=3 or not all(math.isfinite(x) for x in values):raise ValueError('Expected three finite components')
 if not 0<math.hypot(*values)<math.inf:raise ValueError('Zero or unrepresentable normal length')
 return values

def unit(value):
 value=vector(value);length=math.hypot(*value);return tuple(x/length for x in value)

def angular_degrees(a,b):
 """Stable near zero and180 degrees, with separate length diagnostics elsewhere."""
 a=unit(a);b=unit(b)
 cross=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
 return math.degrees(math.atan2(math.sqrt(sum(x*x for x in cross)),sum(x*y for x,y in zip(a,b))))

def compare_normals(expected,actual,geometric=None,*,component_limit=None,angle_limit_degrees=None,unit_error_limit=None,geometric_angle_limit_degrees=None,expected_geometric_limit_degrees=None):
 """Measure corresponding vectors; optional joint bounds are case-specific, not defaults.

 The caller must prove corner/topology correspondence first. This helper does not
 save, repair, quantize, assign normals or establish their source/bit encoding.
 """
 expected=list(expected);actual=list(actual);geometric=list(geometric) if geometric is not None else None
 if not expected or len(expected)!=len(actual) or geometric is not None and len(geometric)!=len(actual):raise ValueError('Equal nonempty corresponding arrays required')
 limits=(component_limit,angle_limit_degrees,unit_error_limit,geometric_angle_limit_degrees,expected_geometric_limit_degrees)
 if any(v is not None and (not math.isfinite(v) or v<0) for v in limits):raise ValueError('Finite nonnegative limits required')
 if geometric is None and (geometric_angle_limit_degrees is not None or expected_geometric_limit_degrees is not None):raise ValueError('Geometric reference required for geometric bounds')
 maxima={'componentError':0.,'angleDegrees':0.,'actualUnitLengthError':0.,'actualVsGeometricDegrees':None,'expectedVsGeometricDegrees':None};failed=0;bit_equal=0
 for i,(e,a) in enumerate(zip(expected,actual)):
  e=vector(e);a=vector(a);component=max(abs(x-y) for x,y in zip(e,a));angle=angular_degrees(e,a);length_error=abs(math.hypot(*a)-1)
  maxima['componentError']=max(maxima['componentError'],component);maxima['angleDegrees']=max(maxima['angleDegrees'],angle);maxima['actualUnitLengthError']=max(maxima['actualUnitLengthError'],length_error);bit_equal+=a==e
  values=[component,angle,length_error,None,None]
  if geometric is not None:
   g=vector(geometric[i]);ag=angular_degrees(a,g);eg=angular_degrees(e,g);values[3:]=[ag,eg]
   maxima['actualVsGeometricDegrees']=max(maxima['actualVsGeometricDegrees'] or 0.,ag);maxima['expectedVsGeometricDegrees']=max(maxima['expectedVsGeometricDegrees'] or 0.,eg)
  if any(limit is not None and value>limit for value,limit in zip(values,limits)):failed+=1
 return {'count':len(actual),'exactComponentCount':bit_equal,'maxima':maxima,'failedJointBounds':failed,'boundsSupplied':any(v is not None for v in limits),'passed':failed==0 if any(v is not None for v in limits) else None}
