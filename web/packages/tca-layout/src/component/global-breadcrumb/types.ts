export enum ItemTypes {
  Text = 'text',
  Dropdown = 'dropdown',
  Link = 'link',
  Custom = 'custom',
}

interface BaseItem {
  key?: string;
  replace?: boolean;
  className?: string;
}

export interface TextItem extends BaseItem {
  type: ItemTypes.Text;
  text: string;
}

export interface LinkItem extends BaseItem {
  type: ItemTypes.Link;
  href: string;
  text: string;
}

export interface DropdownItem extends BaseItem {
  type: ItemTypes.Dropdown;
  items: any[];
}

export interface CustomItem extends BaseItem {
  type: ItemTypes.Custom;
  render: () => React.ElementType;
}

export type BreadcrumbItem = TextItem | LinkItem | CustomItem;

export interface GbcState {
  data: BreadcrumbItem[];
}

export const UPDATE_BREADCRUMB_DATA = 'GLOBAL_BREADCRUMB:UPDATE_BREADCRUMB_DATA';
export const EMPTY_BREADCRUMB = 'GLOBAL_BREADCRUMB:EMPTY_BREADCRUMB';

export interface UpdateBreadcrumbData {
  type: typeof UPDATE_BREADCRUMB_DATA;
  payload: BreadcrumbItem[];
}

export interface EmptyBreadcrumb {
  type: typeof EMPTY_BREADCRUMB;
}

export type BreadcrumbActions = UpdateBreadcrumbData | EmptyBreadcrumb;
