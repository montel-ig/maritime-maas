import React, { useState, Fragment } from 'react';
import { Marker, Popup, GeoJSON, Polyline } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';

import { useRoutes } from '../hooks/api-hooks';
import Map from '../../common/map/Map';
import { Stop } from '../stops/Stops';
import styles from './routes.module.css';
import { Route, Shape } from './types';

const Routes = () => {
  const [params, setParams] = useState<string>('');
  const { data, refetch } = useRoutes(params);

  const search = (e: React.SyntheticEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const params = new URLSearchParams(formData as URLSearchParams).toString();
    setParams(params);
    setTimeout(() => {
      refetch();
    }, 200);
  };

  const drawLine = (stops: Stop[]): LatLngExpression[] => {
    return stops.map((stop: Stop) => {
      return [stop.coordinates.latitude, stop.coordinates.longitude];
    });
  };

  const getColorForUUID = (uuid: string): string => {
    return (
      '#' +
      (
        uuid
          .split('')
          .map((s) => s.charCodeAt(0))
          .reduce((a, b) => a * 777 + b, 0) % 0xffffff
      )
        .toString(16)
        .padStart(6, '0')
    );
  };

  return (
    <>
      <h1>Routes</h1>
      <form onSubmit={search} className={styles.form}>
        <label htmlFor="stop_id">Stop id</label>
        <input name="stop_id" className={styles.input} />
        <button type="submit">Search</button>
      </form>
      <Map>
        {data?.map((route: Route) => (
          <Fragment key={route.name + route.id}>
            {route?.stops?.map((stop: Stop) => (
              <Marker
                key={stop.id}
                position={[
                  stop.coordinates.latitude,
                  stop.coordinates.longitude,
                ]}
              >
                <Popup>
                  <p>{stop.id}</p>
                  <p>{stop.name}</p>
                </Popup>
              </Marker>
            ))}
            {route?.shapes.length ? (
              route.shapes.map((shape: Shape) => (
                <GeoJSON
                  key={shape.id}
                  data={shape.geometry}
                  pathOptions={{
                    color: getColorForUUID(shape.id),
                  }}
                />
              ))
            ) : (
              <Polyline
                positions={drawLine(route?.stops)}
                pathOptions={{ color: 'black' }}
              />
            )}
          </Fragment>
        ))}
      </Map>
    </>
  );
};

export default Routes;
