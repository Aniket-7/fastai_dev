#AUTOGENERATED! DO NOT EDIT! File to edit: dev/06_data_source.ipynb (unless otherwise specified).

__all__ = ['DataSource']

from ..imports import *
from ..test import *
from ..core import *
from .core import *
from .transform import *
from .pipeline import *
from ..notebook.showdoc import show_doc

def _mk_subset(self, i):
    tfms = [o.tfms for o in self.tls]
    return TfmdDS(L._gets(self, self.filts[i]), tfms=tfms, do_setup=False, filt=i)

class _FiltTfmdList(TfmdList):
    "Like `TfmdList` but with filters and train/valid attribute, for proper setup"
    def __init__(self, dsrc, tfms, do_setup=True):
        self.filt_idx = dsrc.filt_idx
        super().__init__(dsrc.items, tfms, do_setup=do_setup, as_item=True, filt=None)

    def subset(self, i): return _mk_subset(self, i)
    def _get(self, i):
        self.filt = self.filt_idx[i]
        return super()._get(i)

_FiltTfmdList.train,_FiltTfmdList.valid = add_props(lambda i,x: x.subset(i), 2)

class DataSource(TfmdDS):
    "Applies a `tfm` to filtered subsets of `items`"
    def __init__(self, items, tfms=None, filts=None, do_setup=True):
        super(TfmdDS,self).__init__(items, use_list=None)
        if filts is None: filts = [range_of(items)]
        self.filts = L(mask2idxs(filt) for filt in filts)

        # Create map from item id to filter id
        assert all_disjoint(self.filts)
        self.filt_idx = L([None]*len(self.items))
        for i,f in enumerate(self.filts): self.filt_idx[f] = i
        self.tls = [_FiltTfmdList(self, t, do_setup=do_setup) for t in L(tfms)]

    def __repr__(self): return '\n'.join(map(str,self.subsets())) + f'\ntls - {self.tls}'
    def subsets(self): return map(self.subset, range_of(self.filts))
    def subset(self, i): return _mk_subset(self, i)
    def _get(self, i):
        self.filt = self.filt_idx[i]
        return super()._get(i)

    @delegates(TfmdDL.__init__)
    def databunch(self, bs=16, val_bs=None, shuffle_train=True, **kwargs):
        n = len(self.filts)-1
        bss = [bs] + [2*bs]*n if val_bs is None else [bs] + [val_bs]*n
        shuffles = [shuffle_train] + [False]*n
        return DataBunch(*[TfmdDL(self.subset(i), bs=b, shuffle=s, drop_last=s, **kwargs)
                           for i,(b,s) in enumerate(zip(bss, shuffles))])

DataSource.train,DataSource.valid = add_props(lambda i,x: x.subset(i), 2)