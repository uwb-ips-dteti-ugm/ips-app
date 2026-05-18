"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useActionState, useCallback, useEffect, useState, useTransition } from "react";

import { initialActionState, type ActionState } from "@/lib/actions/form";
import { formatDate } from "@/lib/format";
import editIcon from "@/shared/assets/EditIcon.svg";
import infoIcon from "@/shared/assets/InfoIcon.svg";
import permissionAssignIcon from "@/shared/assets/PermissionAssignIcon.svg";
import trashIcon from "@/shared/assets/TrashIcon.svg";
import { DescriptionList, DescriptionRow } from "@/shared/components/DescriptionList";
import { FilterBar } from "@/shared/components/FilterBar";
import { ActionMessage, SelectField, TextField } from "@/shared/components/FormControls";
import { Modal, ModalActions } from "@/shared/components/Modal";
import { Pagination } from "@/shared/components/Pagination";
import {
  DataTable,
  EmptyTableState,
  IconActionButton,
  RowActions,
  TableBadge,
  TableCell,
  TableHead,
  TableLoadingOverlay,
} from "@/shared/components/Table";

const SEARCH_DEBOUNCE_MS = 400;

export type ResourcePermissionItem = {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string | null;
  version: number;
};

export type ResourceItem = {
  id: string;
  name: string;
  description: string;
  is_default?: boolean;
  permissions?: ResourcePermissionItem[];
  created_at: string;
  updated_at: string | null;
  version: number;
};

export type ResourceMeta = {
  page: number;
  limit: number;
  total: number;
};

type ResourceAction = (
  state: ActionState,
  formData: FormData,
) => Promise<ActionState>;

type ResourcePageContentProps<TItem extends ResourceItem> = {
  items: TItem[];
  meta: ResourceMeta;
  search: string;
  resourceLabel: string;
  resourceLabelPlural: string;
  emptyMessage: string;
  canCreate: boolean;
  canManage: boolean;
  canDelete: boolean;
  canAssignPermissions?: boolean;
  showDefault?: boolean;
  showPermissions?: boolean;
  allPermissions?: ResourcePermissionItem[];
  createAction: ResourceAction;
  updateAction: ResourceAction;
  deleteAction: ResourceAction;
  assignPermissionsAction?: ResourceAction;
};

type ActiveResourceModal<TItem extends ResourceItem> =
  | { type: "create" }
  | { type: "info"; item: TItem }
  | { type: "edit"; item: TItem }
  | { type: "delete"; item: TItem }
  | { type: "permissions"; item: TItem }
  | null;

export function ResourcePageContent<TItem extends ResourceItem>({
  items,
  meta,
  search,
  resourceLabel,
  resourceLabelPlural,
  emptyMessage,
  canCreate,
  canManage,
  canDelete,
  canAssignPermissions = false,
  showDefault = false,
  showPermissions = false,
  allPermissions = [],
  createAction,
  updateAction,
  deleteAction,
  assignPermissionsAction,
}: ResourcePageContentProps<TItem>) {
  const [isTableLoading, setIsTableLoading] = useState(false);
  const [activeModal, setActiveModal] =
    useState<ActiveResourceModal<TItem>>(null);
  const closeModal = useCallback(() => setActiveModal(null), []);

  return (
    <>
      <ResourceFilters
        search={search}
        limit={meta.limit}
        resourceLabel={resourceLabel}
        canCreate={canCreate}
        onCreate={() => setActiveModal({ type: "create" })}
        onTableLoadingChange={setIsTableLoading}
      />

      <section className="overflow-hidden rounded-md border border-[#D9EEF7] bg-white dark:border-[#1C4D8D] dark:bg-[#07111F]">
        <div className="relative">
          <ResourceTable
            items={items}
            emptyMessage={emptyMessage}
            showDefault={showDefault}
            showPermissions={showPermissions}
            canManage={canManage}
            canDelete={canDelete}
            canAssignPermissions={
              canAssignPermissions &&
              Boolean(assignPermissionsAction) &&
              allPermissions.length > 0
            }
            onInfo={(item) => setActiveModal({ type: "info", item })}
            onEdit={(item) => setActiveModal({ type: "edit", item })}
            onDelete={(item) => setActiveModal({ type: "delete", item })}
            onPermissions={(item) => setActiveModal({ type: "permissions", item })}
          />
          {isTableLoading && (
            <TableLoadingOverlay label={`Loading ${resourceLabelPlural}`} />
          )}
        </div>

        <ResourcePagination
          page={meta.page}
          limit={meta.limit}
          total={meta.total}
          search={search}
          itemLabel={resourceLabelPlural}
          onTableLoadingChange={setIsTableLoading}
        />
      </section>

      {activeModal?.type === "create" && (
        <ResourceFormModal
          title={`Register ${resourceLabel}`}
          submitLabel="Register"
          pendingLabel="Registering"
          action={createAction}
          onClose={closeModal}
        />
      )}
      {activeModal?.type === "info" && (
        <ResourceInfoModal
          item={activeModal.item}
          title={`${resourceLabel} Info`}
          showDefault={showDefault}
          showPermissions={showPermissions}
          onClose={closeModal}
        />
      )}
      {activeModal?.type === "edit" && (
        <ResourceFormModal
          item={activeModal.item}
          title={`Edit ${resourceLabel}`}
          submitLabel="Save"
          pendingLabel="Saving"
          action={updateAction}
          onClose={closeModal}
        />
      )}
      {activeModal?.type === "delete" && (
        <ResourceDeleteModal
          item={activeModal.item}
          resourceLabel={resourceLabel}
          action={deleteAction}
          onClose={closeModal}
        />
      )}
      {activeModal?.type === "permissions" && assignPermissionsAction && (
        <PermissionAssignmentModal
          item={activeModal.item}
          resourceLabel={resourceLabel}
          permissions={allPermissions}
          action={assignPermissionsAction}
          onClose={closeModal}
        />
      )}
    </>
  );
}

function ResourceFilters({
  search,
  limit,
  resourceLabel,
  canCreate,
  onCreate,
  onTableLoadingChange,
}: {
  search: string;
  limit: number;
  resourceLabel: string;
  canCreate: boolean;
  onCreate: () => void;
  onTableLoadingChange: (isLoading: boolean) => void;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchValue, setSearchValue] = useState(search);
  const [, startTransition] = useTransition();

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      const normalizedSearch = searchValue.trim();
      const currentSearch = searchParams.get("search") ?? "";

      if (normalizedSearch === currentSearch) {
        return;
      }

      replaceResourceQuery({
        pathname,
        router,
        searchParams,
        search: normalizedSearch,
        limit,
        onTableLoadingChange,
        startTransition,
      });
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [
    limit,
    onTableLoadingChange,
    pathname,
    router,
    searchParams,
    searchValue,
    startTransition,
  ]);

  return (
    <FilterBar>
      <TextField
        id="resource-search"
        label="Search"
        name="search"
        type="search"
        value={searchValue}
        onChange={(event) => {
          const nextSearch = event.currentTarget.value;
          setSearchValue(nextSearch);
          onTableLoadingChange(
            nextSearch.trim() !== (searchParams.get("search") ?? ""),
          );
        }}
        placeholder={`Search ${resourceLabel.toLowerCase()}s`}
        className="min-w-[220px] flex-1"
        inputClassName="w-full min-w-0"
      />

      <SelectField
        id="resource-limit"
        label="Entries"
        name="limit"
        value={String(limit)}
        onChange={(event) =>
          replaceResourceQuery({
            pathname,
            router,
            searchParams,
            search: searchValue.trim(),
            limit: Number.parseInt(event.currentTarget.value, 10),
            onTableLoadingChange,
            startTransition,
          })
        }
        className="w-24"
      >
        <option value="10">10</option>
        <option value="20">20</option>
        <option value="50">50</option>
      </SelectField>

      {canCreate && (
        <button
          type="button"
          onClick={onCreate}
          className="ml-auto flex h-10 items-center justify-center self-end whitespace-nowrap rounded-md bg-[#0F2854] px-4 text-sm font-semibold text-white transition hover:bg-[#1C4D8D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:bg-[#4988C4] dark:hover:bg-[#1C4D8D]"
        >
          + Register
        </button>
      )}
    </FilterBar>
  );
}

function ResourceTable<TItem extends ResourceItem>({
  items,
  emptyMessage,
  showDefault,
  showPermissions,
  canManage,
  canDelete,
  canAssignPermissions,
  onInfo,
  onEdit,
  onDelete,
  onPermissions,
}: {
  items: TItem[];
  emptyMessage: string;
  showDefault: boolean;
  showPermissions: boolean;
  canManage: boolean;
  canDelete: boolean;
  canAssignPermissions: boolean;
  onInfo: (item: TItem) => void;
  onEdit: (item: TItem) => void;
  onDelete: (item: TItem) => void;
  onPermissions: (item: TItem) => void;
}) {
  if (items.length === 0) {
    return <EmptyTableState message={emptyMessage} />;
  }

  return (
    <DataTable>
      <thead className="bg-[#EAF6FB] text-xs uppercase text-[#1C4D8D] dark:bg-[#0B1E38] dark:text-[#BDE8F5]">
        <tr>
          <TableHead>Name</TableHead>
          <TableHead>Description</TableHead>
          {showPermissions && <TableHead>Permissions</TableHead>}
          {showDefault && <TableHead>Default</TableHead>}
          <TableHead>Updated</TableHead>
          <TableHead>Actions</TableHead>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr
            key={item.id}
            className="border-b border-[#D9EEF7] last:border-b-0 dark:border-[#1C4D8D]"
          >
            <TableCell>
              <div className="max-w-64 truncate font-semibold text-[#0F2854] dark:text-white">
                {item.name}
              </div>
            </TableCell>
            <TableCell>
              <div className="max-w-96 truncate">
                {item.description || "No description"}
              </div>
            </TableCell>
            {showPermissions && (
              <TableCell className="text-center">
                <TableBadge className="border-[#4988C4]/40 bg-[#BDE8F5]/50 text-[#0F2854] dark:text-[#BDE8F5]">
                  {item.permissions?.length ?? 0}
                </TableBadge>
              </TableCell>
            )}
            {showDefault && (
              <TableCell className="text-center">
                {item.is_default ? "Yes" : "No"}
              </TableCell>
            )}
            <TableCell>{formatDate(item.updated_at)}</TableCell>
            <TableCell className="text-center">
              <RowActions>
                <IconActionButton
                  icon={infoIcon}
                  label="Info"
                  onClick={() => onInfo(item)}
                />
                {canAssignPermissions && (
                  <IconActionButton
                    icon={permissionAssignIcon}
                    label="Permissions"
                    onClick={() => onPermissions(item)}
                  />
                )}
                {canManage && (
                  <IconActionButton
                    icon={editIcon}
                    label="Edit"
                    onClick={() => onEdit(item)}
                  />
                )}
                {canDelete && (
                  <IconActionButton
                    icon={trashIcon}
                    label="Delete"
                    onClick={() => onDelete(item)}
                    variant="danger"
                  />
                )}
              </RowActions>
            </TableCell>
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}

function ResourcePagination({
  page,
  limit,
  total,
  search,
  itemLabel,
  onTableLoadingChange,
}: {
  page: number;
  limit: number;
  total: number;
  search: string;
  itemLabel: string;
  onTableLoadingChange: (isLoading: boolean) => void;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  return (
    <Pagination
      page={page}
      limit={limit}
      total={total}
      itemLabel={itemLabel}
      busy={isPending}
      onPageChange={(nextPage) =>
        goToResourcePage({
          page: nextPage,
          limit,
          search,
          onTableLoadingChange,
          pathname,
          router,
          searchParams,
          startTransition,
        })
      }
    />
  );
}

function ResourceFormModal<TItem extends ResourceItem>({
  item,
  title,
  submitLabel,
  pendingLabel,
  action,
  onClose,
}: {
  item?: TItem;
  title: string;
  submitLabel: string;
  pendingLabel: string;
  action: ResourceAction;
  onClose: () => void;
}) {
  const [state, formAction, pending] = useActionState(action, initialActionState);
  useCloseOnSuccess(state, onClose);

  return (
    <Modal title={title} onClose={onClose}>
      <form action={formAction} className="flex flex-col gap-4">
        {item && <input type="hidden" name="id" value={item.id} />}
        <div className="flex flex-col gap-4">
          <TextField
            label="Name"
            name="name"
            defaultValue={item?.name ?? ""}
            required
          />
          <TextField
            label="Description"
            name="description"
            defaultValue={item?.description ?? ""}
          />
        </div>

        <ActionMessage state={state} />

        <ModalActions
          submitLabel={submitLabel}
          pendingLabel={pendingLabel}
          pending={pending}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

function ResourceInfoModal<TItem extends ResourceItem>({
  item,
  title,
  showDefault,
  showPermissions,
  onClose,
}: {
  item: TItem;
  title: string;
  showDefault: boolean;
  showPermissions: boolean;
  onClose: () => void;
}) {
  return (
    <Modal title={title} onClose={onClose}>
      <DescriptionList>
        <DescriptionRow label="Name" value={item.name} />
        <DescriptionRow
          label="Description"
          value={item.description || "No description"}
        />
        {showDefault && (
          <DescriptionRow
            label="Default"
            value={item.is_default ? "Yes" : "No"}
          />
        )}
        {showPermissions && (
          <DescriptionRow
            label="Permissions"
            value={
              item.permissions && item.permissions.length > 0
                ? item.permissions.map((permission) => permission.name).join(", ")
                : "No permissions"
            }
          />
        )}
        <DescriptionRow label="Created" value={formatDate(item.created_at)} />
        <DescriptionRow label="Updated" value={formatDate(item.updated_at)} />
        <DescriptionRow label="Version" value={String(item.version)} />
      </DescriptionList>
    </Modal>
  );
}

function ResourceDeleteModal<TItem extends ResourceItem>({
  item,
  resourceLabel,
  action,
  onClose,
}: {
  item: TItem;
  resourceLabel: string;
  action: ResourceAction;
  onClose: () => void;
}) {
  const [state, formAction, pending] = useActionState(action, initialActionState);
  useCloseOnSuccess(state, onClose);

  return (
    <Modal title={`Delete ${resourceLabel}`} onClose={onClose} widthClassName="max-w-md">
      <form action={formAction} className="flex flex-col gap-4">
        <input type="hidden" name="id" value={item.id} />
        <p className="text-sm leading-6 text-[#0F2854] dark:text-white">
          Delete <span className="font-semibold">{item.name}</span>? This action
          cannot be undone.
        </p>

        <ActionMessage state={state} />

        <ModalActions
          submitLabel="Delete"
          pendingLabel="Deleting"
          pending={pending}
          onClose={onClose}
          destructive
        />
      </form>
    </Modal>
  );
}

function PermissionAssignmentModal<TItem extends ResourceItem>({
  item,
  resourceLabel,
  permissions,
  action,
  onClose,
}: {
  item: TItem;
  resourceLabel: string;
  permissions: ResourcePermissionItem[];
  action: ResourceAction;
  onClose: () => void;
}) {
  const [state, formAction, pending] = useActionState(action, initialActionState);
  useCloseOnSuccess(state, onClose);
  const assignedPermissionIds = new Set(
    item.permissions?.map((permission) => permission.id) ?? [],
  );

  return (
    <Modal title={`${resourceLabel} Permissions`} onClose={onClose}>
      <form action={formAction} className="flex flex-col gap-4">
        <input type="hidden" name="id" value={item.id} />
        {item.permissions?.map((permission) => (
          <input
            key={permission.id}
            type="hidden"
            name="assigned_permission_ids"
            value={permission.id}
          />
        ))}

        <div className="max-h-80 overflow-y-auto rounded-md border border-[#D9EEF7] dark:border-[#1C4D8D]">
          {permissions.map((permission) => (
            <label
              key={permission.id}
              className="flex cursor-pointer items-start gap-3 border-b border-[#D9EEF7] px-3 py-3 last:border-b-0 dark:border-[#1C4D8D]"
            >
              <input
                type="checkbox"
                name="permission_ids"
                value={permission.id}
                defaultChecked={assignedPermissionIds.has(permission.id)}
                className="mt-1 h-4 w-4 rounded border-[#4988C4] text-[#1C4D8D] focus:ring-[#4988C4]"
              />
              <span className="min-w-0">
                <span className="block text-sm font-semibold text-[#0F2854] dark:text-white">
                  {permission.name}
                </span>
                {permission.description && (
                  <span className="block text-xs text-[#4988C4] dark:text-[#BDE8F5]">
                    {permission.description}
                  </span>
                )}
              </span>
            </label>
          ))}
        </div>

        <ActionMessage state={state} />

        <ModalActions
          submitLabel="Save"
          pendingLabel="Saving"
          pending={pending}
          onClose={onClose}
        />
      </form>
    </Modal>
  );
}

function replaceResourceQuery({
  pathname,
  router,
  searchParams,
  search,
  limit,
  onTableLoadingChange,
  startTransition,
}: {
  pathname: string;
  router: ReturnType<typeof useRouter>;
  searchParams: ReturnType<typeof useSearchParams>;
  search: string;
  limit: number;
  onTableLoadingChange: (isLoading: boolean) => void;
  startTransition: (callback: () => void) => void;
}) {
  const nextSearchParams = new URLSearchParams(searchParams.toString());
  nextSearchParams.set("page", "0");
  nextSearchParams.set("limit", String(limit));

  if (search) {
    nextSearchParams.set("search", search);
  } else {
    nextSearchParams.delete("search");
  }

  replaceQuery({
    nextSearchParams,
    currentQuery: searchParams.toString(),
    pathname,
    router,
    onTableLoadingChange,
    startTransition,
  });
}

function goToResourcePage({
  page,
  limit,
  search,
  onTableLoadingChange,
  pathname,
  router,
  searchParams,
  startTransition,
}: {
  page: number;
  limit: number;
  search: string;
  onTableLoadingChange: (isLoading: boolean) => void;
  pathname: string;
  router: ReturnType<typeof useRouter>;
  searchParams: ReturnType<typeof useSearchParams>;
  startTransition: (callback: () => void) => void;
}) {
  const guardedPage = Math.max(1, page);
  const nextSearchParams = new URLSearchParams(searchParams.toString());
  nextSearchParams.set("page", String(guardedPage - 1));
  nextSearchParams.set("limit", String(limit));

  if (search) {
    nextSearchParams.set("search", search);
  } else {
    nextSearchParams.delete("search");
  }

  replaceQuery({
    nextSearchParams,
    currentQuery: searchParams.toString(),
    pathname,
    router,
    onTableLoadingChange,
    startTransition,
  });
}

function replaceQuery({
  nextSearchParams,
  currentQuery,
  pathname,
  router,
  onTableLoadingChange,
  startTransition,
}: {
  nextSearchParams: URLSearchParams;
  currentQuery: string;
  pathname: string;
  router: ReturnType<typeof useRouter>;
  onTableLoadingChange: (isLoading: boolean) => void;
  startTransition: (callback: () => void) => void;
}) {
  const nextQuery = nextSearchParams.toString();

  if (nextQuery === currentQuery) {
    onTableLoadingChange(false);
    return;
  }

  onTableLoadingChange(true);
  startTransition(() => {
    router.replace(`${pathname}?${nextQuery}`, { scroll: false });
  });
}

function useCloseOnSuccess(state: ActionState, onClose: () => void) {
  const router = useRouter();

  useEffect(() => {
    if (state.status !== "success") {
      return;
    }

    onClose();
    router.refresh();
  }, [onClose, router, state.status]);
}
