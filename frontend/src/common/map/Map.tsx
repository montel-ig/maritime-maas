import React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import { LatLngTuple } from 'leaflet';

import styles from './map.module.css';

type Props = {
  children: React.ReactElement | null;
};

const Map = ({ children }: Props) => {
  const center: LatLngTuple = [60.152222, 24.956048];

  return (
    <div className={styles.container}>
      <MapContainer center={center} zoom={8} className={styles.map}>
        <TileLayer
          attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {children}
      </MapContainer>
    </div>
  );
};

export default Map;
