import localforage from 'localforage';

export interface MediaMetadata {
  id: string;
  name: string;
  type: string;
  size: number;
  lastModified: number;
  loopCount: number;
  savedLoops: Array<{ name: string; start: number; end: number }>;
}

const mediaStore = localforage.createInstance({
  name: 'wgetube',
  storeName: 'media_metadata'
});

export const saveMediaMetadata = async (metadata: MediaMetadata) => {
  await mediaStore.setItem(metadata.id, metadata);
};

export const getMediaMetadata = async (id: string): Promise<MediaMetadata | null> => {
  return await mediaStore.getItem(id);
};

export const getAllMedia = async (): Promise<MediaMetadata[]> => {
  const keys = await mediaStore.keys();
  const items = await Promise.all(keys.map(key => mediaStore.getItem(key)));
  return items.filter((item): item is MediaMetadata => item !== null);
};

export const incrementLoopCount = async (id: string) => {
  const metadata = await getMediaMetadata(id);
  if (metadata) {
    metadata.loopCount += 1;
    await saveMediaMetadata(metadata);
  }
};
