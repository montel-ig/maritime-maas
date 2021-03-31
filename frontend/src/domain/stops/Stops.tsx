import React, { useState } from 'react';
import { Marker, Popup } from 'react-leaflet';

import Map from '../../common/map/Map';
import { useStops } from '../hooks/api-hooks';
import styles from './stops.module.css';

export type Stop = {
  id: number;
  name: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
};

const Stops = () => {
  const [params, setParams] = useState<string>('');
  const { data, refetch } = useStops(params);

  const search = (e: React.SyntheticEvent) => {
    e.preventDefault();
    const target = e.target as typeof e.target & {
      location: { value: string };
      radius: { value: number };
    };
    const location = target.location.value;
    const radius = target.radius.value;
    const params = `?location=${location}&radius=${radius}`;
    setParams(params);
    setTimeout(() => {
      refetch();
    }, 200);
  };

  return (
    <div>
      <h1>Stops</h1>
      <form onSubmit={search} className={styles.form}>
        <label htmlFor="location">Location</label>
        <input name={'location'} className={styles.input} />
        <label htmlFor="radius">Radius</label>
        <input name={'radius'} className={styles.input} />
        <button type="submit">Search</button>
      </form>

      <Map>
        {data?.map((stop: Stop) => (
          <Marker
            key={stop.id}
            position={[stop.coordinates.latitude, stop.coordinates.longitude]}
          >
            <Popup>
              <p>{stop.id}</p>
              <p>{stop.name}</p>
            </Popup>
          </Marker>
        ))}
      </Map>
    </div>
  );
};

export default Stops;
