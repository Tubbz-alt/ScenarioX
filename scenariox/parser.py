#!/usr/bin/env python3
import uuid
import re

class Parser():
    pfile = None
    pfile_delim = None
    pfile_lines = None
    pfile_map = None

    gmap = None
    
    phases = None
    
    def __init__(self, f, delim = '\t', pformat = "gformat"):
        self.pfile = f
        self.poutput = 'json'
        self.pfile_delim = delim
        self.phases = {}
        self.ReadFile()
        self.MapHeader()
        if pformat == 'gformat':
            self.GPhases()
        
    def ReadFile(self):
        if self.pfile:
            self.pfile_lines = [i.replace('\n','').replace('\r','').lower().split(self.pfile_delim) for i in open(self.pfile).readlines()]
        return self
    
    def MapHeader(self):
        if self.pfile_lines:
            self.pfile_map = {self.pfile_lines[0][i] : i for i in range(len(self.pfile_lines[0]))}
        return self

    def GPhases(self, subdelim = '-'):
        if self.pfile_lines and self.pfile_map:
            self.phases['root'] = self.Phase(self, "root", [], None, None)
            deps = ['root']
            pid = None
            duration = None
            comms = None
            for i in self.pfile_lines[1:]:
                deps = i[self.pfile_map['dependency']].split(',') if i[self.pfile_map['dependency']] != '' else (['root'] if i[self.pfile_map['cell']] == '' else deps)
                duration = self.GDate([i[self.pfile_map['minimum duration']], i[self.pfile_map['maximum duration']]], i[self.pfile_map['time unit']]) if i[self.pfile_map['maximum duration']] != '' and i[self.pfile_map['minimum duration']] != '' else duration
                if not i[0] in self.pfile_map.keys() and i[self.pfile_map['cell']] != '':
                    pid = i[self.pfile_map['cell']]
                    comms = [{'channel' : i[self.pfile_map['channel']],
                              'p1_range' : [int(i[self.pfile_map['minimum sender']]), int(i[self.pfile_map['maximum sender']])],
                              'p1_title' : i[self.pfile_map['sender type']],
                              'direction' : i[self.pfile_map['direction']],
                              'p2_range' : [int(i[self.pfile_map['minimum recipient']]), int(i[self.pfile_map['maximum recipient']])],
                              'p2_title' : i[self.pfile_map['recipient type']],
                              'comms_range' : [int(i[self.pfile_map['minimum transactions']]), int(i[self.pfile_map['maximum transactions']])],
                              'description' : i[self.pfile_map['observable/description']],
                              }]
                    for j in range(len(deps)):
                        val = deps.pop(0)
                        if val in self.phases.keys():
                            deps += [val]
                        else:
                            for k in self.phases.keys():
                                subval = k.replace(val + subdelim,'')
                                if subval.isdigit():
                                    deps += [val + subdelim + subval]
                    phase = self.Phase(self, pid, deps, duration, comms)
                    if pid in self.phases.keys():
                        self.phases[pid].comms += comms
                    else:
                        self.phases[pid] = phase
        return self

    def GDate(self, nums, unit):
        if len(nums) == 2:
            if 'day' in unit:
                return [int(i) * 86400 for i in nums]
            if 'week' in unit:
                return [int(i) * 604800 for i in nums]
            if 'month' in unit:
                return [int(i) * 2628000 for i in nums]
            if 'year' in unit:
                return [int(i) * 31540000 for i in nums]
            return nums
        return None

    def GRange(self, inval):
        nums = re.findall(r'\d+(?: \d+)?', inval)
        return [int(i) for i in nums]

    def GTitle(self, comms):
        title = ' '.join(''.join([i for i in comms if not i.isdigit()]).strip(' ').split(' ')[1:])
        return title
    
    class Phase():
        outer = None
        uid = None
        pid = None
        parents = None
        children = None
        duration = None
        comms = None
        
        def __init__(self, outer, pid, depends, duration, comms):
            self.pid = pid
            self.uid = uuid.uuid4()
            self.parents = depends
            self.outer = outer
            self.children = []
            if duration:
                self.duration = {'min' : duration[0], 'max' : duration[1]}
            if comms:
                self.comms = comms
            for i in self.parents:
                self.outer.phases[i].children += [self.pid]
                
        def depends(self):
            for i in self.parents:
                yield self.outer.phases[i]

        def proceeds(self):
            for i in self.children:
                yield self.outer.phases[i]

