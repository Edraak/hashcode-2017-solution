from __future__ import division

import operator


class Item(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        for key, val in kwargs.iteritems():
            if key in self.props:
                setattr(self, key, val)
            else:
                raise Exception('Sure? {} {} {}'.format(self.__class__.__name__, key, val))

    def __repr__(self):
        return '<{cls}: {kwargs}>'.format(
            cls=self.__class__.__name__,
            kwargs=self.kwargs,
        )


class Video(Item):
    props = ['id', 'size', 'possible_caches']
    id = None
    size = None
    possible_caches = None


class Endpoint(Item):
    props = ['id', 'dc_latency', 'caches_count', 'caches_latencies']
    id = None
    dc_latency = None
    caches_count = None
    caches_latencies = None


class Cache(Item):
    props = ['id', 'size', 'stored_videos', 'endpoints', 'possible_videos', 'sorted_possible_videos', 'done',
             'first_time']
    id = None
    size = None
    stored_videos = None
    endpoints = None
    possible_videos = None
    sorted_possible_videos = None
    done = None
    first_time = True

    def rescore(self, video_id, ep_id, count, video_cache):

        if video_id in self.possible_videos:
            old_score = (w.endpoints[ep_id].dc_latency - w.endpoints[ep_id].caches_latencies[self.id]) * count * (w.cache_size_mb / w.videos[video_id].size)
            new_score = (w.endpoints[ep_id].caches_latencies[video_cache.id] - w.endpoints[ep_id].caches_latencies[self.id]) * count * (w.cache_size_mb / w.videos[video_id].size)
            self.possible_videos[video_id].score -= old_score - new_score


class CachePossibleVideo(Item):
    props = ['video_id', 'score', 'endpoints']
    video_id = None
    score = None
    endpoints = None

class World(object):
    videos = []
    endpoints = []
    requests = []
    caches = []

    cache_size_mb = videos_count = endpoints_count = caches_count = reqs_count = None


# ============ ALI START =============


    def solve(self):
        pass

    def process_requests(self, line_iter):
        for req_id in range(self.reqs_count):
            endpoint_desc_line = next(line_iter).strip()
            video_id, endpoint_id, count = map(int, endpoint_desc_line.split(' '))
            endpoint = self.endpoints[endpoint_id]
            for cache_id, cache_lat in endpoint.caches_latencies.iteritems():
                score = (endpoint.dc_latency - cache_lat) * count * (self.cache_size_mb / self.videos[video_id].size)
                _possible_videos = self.caches[cache_id].possible_videos
                if video_id in _possible_videos:
                    # Increase score
                    _possible_videos[video_id].score += score
                    _possible_videos[video_id].endpoints[endpoint_id] = count
                else:
                    _possible_videos[video_id] = CachePossibleVideo(score=score, endpoints={endpoint_id: count},
                                                                    video_id=video_id)


    def process_caches(self):
        all_done = True
        for cache in self.caches:
            print str(cache.id),
            if cache.done:
                continue
            all_done = False
            if cache.first_time:
                cache.sorted_possible_videos = list(cache.possible_videos.values())
                cache.first_time = False
                cache.sorted_possible_videos.sort(key=lambda t: t.score, reverse=True)
            else:
                cache.sorted_possible_videos.sort(key=lambda t: t.score, reverse=True)

            for i, possible_video in enumerate(cache.sorted_possible_videos):
                if cache.size - self.videos[possible_video.video_id].size >= 0:
                    cache.size -= self.videos[possible_video.video_id].size
                    cache.stored_videos[possible_video.video_id] = self.videos[possible_video.video_id]
                    for ep_id, count in possible_video.endpoints.iteritems():
                        for cache_id, cache_lat in self.endpoints[ep_id].caches_latencies.iteritems():
                            if cache_id != cache.id:
                                self.caches[cache_id].rescore(possible_video.video_id, ep_id, count, cache)
                    del cache.sorted_possible_videos[i]
                    del cache.possible_videos[possible_video.video_id]
                    break
                else:
                    if i == len(cache.sorted_possible_videos) - 1:
                        cache.done = True
        return all_done

    def output_result(self, filename):
        with open(filename, 'w') as file_obj:
            file_obj.write(str(len(self.caches)) + "\n")
            for cache in w.caches:
                file_obj.write(str(cache.id) + " ")
                for vid, v in cache.stored_videos.iteritems():
                    file_obj.write(str(vid) + " ")
                file_obj.write("\n")


# ============ ALI END =============

    @staticmethod
    def insertionSort(L, reverse=False):
        lt = operator.gt if reverse else operator.lt
        for j in xrange(1, len(L)):
            valToInsert = L[j]
            i = j - 1
            while 0 <= i and lt(valToInsert.score, L[i].score):
                L[i + 1] = L[i]
                i -= 1
            L[i + 1] = valToInsert

    @staticmethod
    def from_file(file_obj):
        obj = World()
        line_iter = iter(file_obj)

        counts_line = next(line_iter).strip()

        obj.videos_count, obj.endpoints_count, obj.reqs_count, obj.caches_count, obj.cache_size_mb = map(int, counts_line.split(' '))

        videos_line = next(line_iter).strip()
        obj.videos = tuple(
            Video(id=index, size=int(size_mb), possible_caches={})
            for index, size_mb in enumerate(videos_line.split(' '))
        )

        obj.caches = tuple(
            Cache(id=index, size=obj.cache_size_mb, stored_videos={}, endpoints={}, possible_videos={},
                  sorted_possible_videos=[], done=False, first_time=True)
            for index in range(obj.caches_count)
        )

        for endpoint_id in range(obj.endpoints_count):
            endpoint_desc_line = next(line_iter).strip()
            dc_latency, caches_count = map(int, endpoint_desc_line.split(' '))
            endpoint = Endpoint(id=endpoint_id, dc_latency=dc_latency, caches_count=caches_count, caches_latencies={})
            obj.endpoints.append(endpoint)

            for cache in range(caches_count):
                cache_desc_line = next(line_iter).strip()
                cache_id, latency = map(int, cache_desc_line.split(' '))
                endpoint.caches_latencies[cache_id] = latency
                obj.caches[cache_id].endpoints[endpoint_id] = latency

        obj.process_requests(line_iter)

        return obj


from sys import argv
filename = argv[1]
with open(filename) as file_obj:
    print 'Start', filename
    w = World.from_file(file_obj)
    # w.process_requests()
    count = 1
    print "************** Processing all #", count, "**************\nProcessing Cache # ",
    while not w.process_caches():
        print
        print "Done Processing all #", count
        print "Caches remaining size",
        for cache in w.caches:
            print "Full" if cache.done else cache.size,
        count += 1
        print
        print "************** Processing all #", count, "**************\nProcessing Cache # ",
    w.output_result(filename.replace('.in', '.out'))
    print 'Done', filename
