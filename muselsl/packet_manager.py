import numpy as np


class PacketsManager():
    def __init__(self, handles, bad_channels=[], buffer_size=5):
        self.packets = [None] * buffer_size
        self.handles = handles
        self.bad_channels = bad_channels
        self.buffer_size = buffer_size

    def push_data(self, packet_index, handle, timestamp, data):
        packet_list_index = packet_index % self.buffer_size
        packet = self.packets[packet_list_index]

        if packet and packet.packet_index != packet_index:
            print(f'Buffer reached limit of {self.buffer_size} items, dropping packet.')
            packet = None

        if packet is None:
            packet = Packet(packet_index, self.handles, self.bad_channels)
            self.packets[packet_list_index] = packet

        packet.push_data(handle, timestamp, data)

        if packet.is_complete:
            self.packets[packet_list_index] = None

        return packet


class Packet():
    def __init__(self, packet_index, handles, bad_channels):
        self.packet_index = packet_index
        self.handles = handles
        self.bad_channels = bad_channels

        self.timestamps = np.full(len(handles), np.nan)
        self.data = np.zeros((len(handles), 12))

    @property
    def channels_indexes(self):
        return [self.handles[handle] for handle in self.handles if not handle in self.bad_channels]

    @property
    def is_complete(self):
        channel_indexes = self.channels_indexes
        # print('timestamps', self.timestamps, list((not np.isnan(self.timestamps[channel_index]) for channel_index in channel_indexes)))
        return all((not np.isnan(self.timestamps[channel_index]) for channel_index in channel_indexes))

    def push_data(self, handle, timestamp, data):
        handle_index = self.handles.get(handle)

        self.timestamps[handle_index] = timestamp
        self.data[handle_index] = data

        # print(self.timestamps)
