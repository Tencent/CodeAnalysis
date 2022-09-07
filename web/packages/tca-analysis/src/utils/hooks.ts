import { useLocation } from 'react-router-dom';

/**
 * 获取当前页面查询参数 hooks
 */
export const useQuery = () => new URLSearchParams(useLocation().search);
