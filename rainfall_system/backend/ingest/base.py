from abc import ABC, abstractmethod
import xarray as xr
import numpy as np

class BaseSource(ABC):
    registry = {}
    
    def __init_subclass__(cls,source_name = None, **kwargs):
        super().__init_subclass__(**kwargs)
            
        if source_name:
            BaseSource.registry[source_name] = cls
        
    def __init__(self, config) -> None:
        super().__init__()
        self.config = config
        self.data = None
        
    
    @abstractmethod
    def fetch(self) -> xr.Dataset:
        pass
        
    @abstractmethod
    def extract(self) -> tuple[xr.DataArray, xr.DataArray,xr.DataArray,xr.DataArray] :
        pass
        
    @abstractmethod
    def process(self):
        pass
    """
    @staticmethod
    def latlon():
        pass
    """

"""

# __init_subclass__ IS the sourcefactory
class SourceFactory:
    registry = {}
    
    @classmethod
    def register(cls, name, source_class ):
        cls.registry[name] = source_class
    
    @classmethod
    def create(cls, name, config):
        if name not in cls.registry:
            raise ValueError(f"name is not in argument")
        return cls.registry[name](config)
"""


    
class WRFSource(BaseSource, source_name = 'WRF'):
    
    def fetch(self):
        """
        fetch data from config url
        """
        path = self.config["path"]
        self.data = xr.open_dataset(path, engine="netcdf4")
        return self.data
    
    def extract(self):
        """
        xarray library to create data frame
        """
        ds = self.data if self.data is not None else self.fetch()
        # ds = self.fetch()
        
        rainc = ds['RAINC']
        rainnc = ds['RAINNC']
        rain = rainc + rainnc
        time = ds['Time']
        lat = ds['XLAT'][0]
        lon = ds['XLONG'][0]
        return rain, time, lat, lon
    
    def speed(self,U,V):
        return np.sqrt(U**2 + V**2)
    
    def direction(self,U,V):
        return (270 - np.degrees(np.arctan2(V,U))) % 360
    
    def latlon(self):
        self.data
        U = self.data["U"]
        V = self.data["V"]
        
        #destagger
        u = 0.5 * (U[:,:,:-1] + U[:,:,1:])
        v = 0.5 * (U[:,:-1,:] + U[:,1:,:])
        
        return u, v
    
    def process(self):
        
        #unstaggered latLon
        u,v = self.latlon()
        
                
        #cummulative rainfall
        [rain, time, lat, lon] = self.extract()
        hourlyRain = rain.diff('Time')
        
    
        