# ---
# jupyter:
#   jupytext:
#     formats: md,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## ai.cs (CXFORM)
#
# This is a wrapper around the cxform package
#
# ```sh
# J2000          Geocentric Equatorial Inertial for epoch J2000.0
#                (GEI2000), also known as Mean Equator and Mean Equinox
#                of J2000.0
# GEO            Geographic, also known as Greenwich Rotating
#                Coordinates (GRC), or Earth-fixed Greenwich (EFG)
# ```

# %%
from kamodo import Kamodo, kamodofy
from ai import cs
import numpy as np

import forge

# %%
from datetime import datetime

# %%
R_e = 6371000 # radius of Earth in m


# %%
def reg_name(from_coord, to_coord, to_superscript=False):
    if to_superscript:
        return f'xvec_{from_coord}__{to_coord}'
    else:
        return f'xvec_{to_coord}'

class CxKamodo(Kamodo):
    def __init__(self, from_coords = ['GEO', 'J2000'], to_coords = ['GEO','J2000'],
                 to_superscript=False, 
                 vectorize=True,
                 time=None,
                 verbose=False,
                 **kwargs):
        """
        Kamodo subclass for transformations between commond space weather coordinate systems
        
        Built on ai.cs, a python wrapper for cxform
        ai.cs https://pypi.org/project/ai.cs/
        cxform https://spdf.gsfc.nasa.gov/pub/software/old/selected_software_from_nssdc/coordinate_transform/
        
        from/to_coords in ['GEI', 'J2000', 'GEO', 'MAG', 'GSE', 'GSM',
        'SM', 'RTN', 'GSEQ', 'HEE', 'HAE', 'HEEQ']
        
        """
        super(CxKamodo, self).__init__(verbose=verbose, **kwargs)
    
        self._from_coords = from_coords
        self._to_coords = to_coords
        self._to_superscript = to_superscript
        self._vectorize = vectorize
        self._time = time
        
        self.register_geometry()
    
        for to_coord in self._to_coords:
            for from_coord in self._from_coords:
                if from_coord != to_coord:
                    regname = reg_name(from_coord, to_coord, to_superscript)
                    self[regname] = self.register_coordinates(from_coord, to_coord)
        
    def register_geometry(self):
        
        @kamodofy
        def xvec(r, theta, phi):
            """convert (r,theta,phi) to (x,y,z)
            
            Note: r theta in [-pi/2, p/2], phi in [0, 2pi]
            """
            return np.array(cs.sp2cart(r, theta, phi))
                
        self['xvec'] = xvec

        @kamodofy
        def rvec(x, y, z):
            """convert (x,y,z) to (r,theta,phi)
            
            Note: r theta in [-pi/2, p/2], phi in [0, 2pi]
            """
            return np.array(cs.cart2sp(x, y, z))

        self['rvec'] = rvec
        
    
    def register_coordinates(self, from_coord, to_coord):
        if from_coord == to_coord:
            return
        
        print(f'registering {from_coord}->{to_coord}')
        
        if self._vectorize:
            xvec_var = f'xvec_{from_coord}'
            t_var = 't'
            signature = [forge.arg(xvec_var),
                        forge.arg(t_var)]
        else:
            x_var = f'x_{from_coord}'
            y_var = f'y_{from_coord}'
            z_var = f'z_{from_coord}'
            t_var = 't'

            signature = [forge.arg(x_var),
                         forge.arg(y_var),
                         forge.arg(z_var),
                         forge.arg(t_var)]

        @forge.sign(*signature)
        def convert(**kwargs):
            """converts in Cartesian"""
            if self._vectorize:
                xvec_ = np.array(kwargs[xvec_var])
                x_, y_, z_ = xvec_.T
                t_ = np.array(kwargs[t_var])
            else:
                x_ = np.array(kwargs[x_var])
                y_ = np.array(kwargs[y_var])
                z_ = np.array(kwargs[z_var])
                t_ = np.array(kwargs[t_var])
            
            if x_.shape != t_.shape:
                if t_.size == 1:
                    t__ = np.tile(t_, x_.shape)
                else:
                    raise NotImplementedError(f"t of shape {t_.shape} not compatible with position x of shape {x_.shape}")
            else:
                t__ = t_

             
            result = np.array(cs.cxform(from_coord, to_coord, t__,
                x=x_,
                y=y_,
                z=z_,)).T
            
            
            return result
        
    
        convert.__name__ = reg_name(from_coord, to_coord, self._to_superscript)
        convert.__doc__ += f" from {from_coord} to {to_coord}\n"
        
        return convert

cx = CxKamodo()
cx