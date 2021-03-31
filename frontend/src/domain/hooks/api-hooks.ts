import { useQuery } from 'react-query';

import { axiosInstance } from '../../common/util/axios';

export const useStops = (params: string) => {
  return useQuery('stops', () =>
    axiosInstance.get(`/v1/stops/?${params}`).then((response) => response.data)
  );
};

export const useRoutes = (params: string) => {
  return useQuery('routes', () =>
    axiosInstance.get(`/v1/routes/?${params}`).then((response) => response.data)
  );
};
