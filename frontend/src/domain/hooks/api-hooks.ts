import { useQuery } from 'react-query';
import axios from 'axios';

export const useStops = (params: string) => {
  return useQuery('stops', () =>
    axios.get(`/v1/stops/${params}`).then((response) => response.data)
  );
};

export const useRoutes = (params: string) => {
  return useQuery('routes', () =>
    axios.get(`/v1/routes/${params}`).then((response) => response.data)
  );
};
