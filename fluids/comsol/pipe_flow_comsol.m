% ===================================================================
% COMSOL Multiphysics Model Script (LiveLink for MATLAB / COMSOL API)
% Simulation of 2D Axisymmetric Laminar Water Flow in a Circular Pipe
% (Developing & Fully Developed Hagen-Poiseuille Flow)
% ===================================================================

import com.comsol.model.*
import com.comsol.model.util.*

% 1. Create Model
model = ModelUtil.create('Model');
model.modelNode.create('comp1');

% 2. Global Parameters
model.param.set('U_in', '67[m/s]', 'Inlet Velocity (Roll Number)');
model.param.set('Re_target', '1600', 'Target Reynolds Number');
model.param.set('rho_w', '998.2[kg/m^3]', 'Water Density at 20 deg C');
model.param.set('mu_w', '1.002e-3[Pa*s]', 'Water Dynamic Viscosity');
model.param.set('nu_w', 'mu_w/rho_w', 'Kinematic Viscosity');
model.param.set('D', 'Re_target*nu_w/U_in', 'Laminar Pipe Diameter');
model.param.set('R', 'D/2', 'Pipe Radius');
model.param.set('Le', '0.0575*Re_target*D', 'Hydrodynamic Entrance Length');
model.param.set('L', '1.6*Le', 'Total Pipe Length');

% 3. Geometry (2D Axisymmetric: r, z)
geom = model.component('comp1').geom.create('geom1', 2);
geom.axisymmetric(true);
r1 = geom.feature.create('r1', 'Rectangle');
r1.set('pos', {'0', '0'});
r1.set('size', {'R', 'L'});
geom.run;

% 4. Material: Water (Liquid)
mat = model.component('comp1').material.create('mat1', 'Common');
mat.name('Water');
mat.propertyGroup('def').set('density', 'rho_w');
mat.propertyGroup('def').set('dynamicviscosity', 'mu_w');
mat.selection.all;

% 5. Physics: Laminar Flow (spf)
spf = model.component('comp1').physics.create('spf', 'LaminarFlow', 'geom1');

% Axial Symmetry on r = 0 (boundary 1) is automatically applied in 2D axisymmetric mode

% Inlet (boundary 2: z = 0)
inlet = spf.feature.create('inl1', 'InletBoundary', 1);
inlet.selection.set([2]);
inlet.set('U0in', 'U_in');

% Outlet (boundary 3: z = L)
outlet = spf.feature.create('out1', 'OutletBoundary', 1);
outlet.selection.set([3]);
outlet.set('p0', '0[Pa]');

% Wall No-Slip (boundary 4: r = R)
% Automatically assigned default no-slip wall condition

% 6. Mesh (Boundary Layer Mesh for near-wall gradient)
mesh = model.component('comp1').mesh.create('mesh1');
mesh.autoMeshSize(2); % Extra Fine
mesh.run;

% 7. Study: Stationary
study = model.study.create('std1');
study.feature.create('stat', 'Stationary');
model.sol.create('sol1');
model.sol('sol1').study('std1');
model.sol('sol1').attach('std1');
model.sol('sol1').createSolution;
model.sol('sol1').runAll;

% 8. Results & Plots
% 2D Velocity Contour Plot
pg1 = model.result.create('pg1', 'PlotGroup2D');
pg1.set('data', 'dset1');
surf = pg1.feature.create('surf1', 'Surface');
surf.set('expr', 'spf.U');
surf.set('unit', 'm/s');
pg1.run;

% Centerline Velocity 1D Plot
pg2 = model.result.create('pg2', 'PlotGroup1D');
pg2.set('data', 'dset1');
line = pg2.feature.create('lng1', 'LineGraph');
line.selection.set([1]); % Centerline axis
line.set('expr', 'w');   % Axial velocity in z
line.set('unit', 'm/s');
pg2.run;

% Save Model File
mphsave(model, 'pipe_flow_comsol.mph');
disp('COMSOL simulation model created and solved successfully.');

