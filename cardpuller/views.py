# views.py
import copy
import math
from django.views.generic import ListView, TemplateView
from .forms import BoxForm, CardFormSet
from .box import box
from django.urls import reverse_lazy
from django.shortcuts import redirect
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import io, base64


class BoxInfoView(TemplateView):
    template_name = "cardpuller/box_info.html"

    def get(self, *args, **kwargs):
        box_form = BoxForm()
        # Create an instance of the formset
        formset = CardFormSet()
        return self.render_to_response({
            'card_formset': formset,
            'box_form': box_form
        })

    def post(self, *args, **kwargs):

        formset = CardFormSet(data=self.request.POST)
        box_form = BoxForm(data=self.request.POST)
        
        # determine the number of packs in the box
        packs = None
        if box_form.is_valid():
            packs = int(box_form.cleaned_data['packs_in_box'])
        this_box = box(packs)
        
        if formset.is_valid():
            # validate that there are enough copies within the box
            index = 0
            extra_by_rarity = this_box.extras.copy()
            rarities_in_order = this_box.rarities
            targets_by_rarity = {}
            form_copy = copy.deepcopy(formset.cleaned_data)
            for card in form_copy:
                # print(card)
                if not targets_by_rarity.get(card['rarity'], False):
                    targets_by_rarity[card['rarity']] = 1
                else:
                    targets_by_rarity[card['rarity']] += 1
                if targets_by_rarity[card['rarity']] > this_box.template['{}_distinct'.format(card['rarity'])]:
                    formset.forms[index].add_error('rarity', 'This box only contains {0} distinct {1}s'.format(this_box.template['{}_distinct'.format(card['rarity'])], card['rarity']))
                in_box = (this_box.template[card['rarity'] + '_total']) / (this_box.template[card['rarity'] + '_distinct'])
                if card.get('extra', False):
                    # makes copy validation work for cards with the 'Extra' attribute
                    in_box = math.ceil(in_box)
                    # now make sure we aren't looking for more 'Extra' cards than are in the box
                    rarity_index = rarities_in_order.index(card['rarity'])
                    if extra_by_rarity[rarity_index] > 0:
                        extra_by_rarity[rarity_index] -= 1
                    else:# too many 'Extra' cards of this rarity
                        formset.forms[index].add_error('extra', "Too many 'Extra' cards of this rarity ({} cards max)".format(this_box.extras[rarity_index]))
                #print(in_box)
                if card['copies'] > in_box:
                    formset.forms[index].add_error('copies', 'Only {} copies in box'.format(int(in_box)))
                index += 1
        
        
        # print(formset.__dict__)
        # formset.forms[0].add_error('Copies', 'test error')
        # for form in formset.forms:
        #     print(type(form))
        # print(formset.forms)

        # Check if submitted forms are valid
        if formset.is_valid():
            self.request.session['size'] = packs
            self.request.session['targets'] = formset.cleaned_data
            self.request.session['trials'] = 1000
            # print(self.request.session._session_cache)
            return redirect(reverse_lazy("sim_info"))
            
        
        return self.render_to_response({
            'card_formset': formset,
            'box_form': box_form,
        })
        
class SimulationResultView(TemplateView):
    template_name = 'cardpuller/sim_info.html'

    def get(self, *args, **kwargs):
        this_box = box(self.request.session['size'])
        trials = self.request.session['trials']
        targets = self.request.session['targets']
        this_box.pick_target_cards(targets)
        this_box.populate()
        results = []
        # repeatedly run our simulation
        for i in range(trials):
            results.append(this_box.pull_for_cards(targets))
            this_box.reset()
            
        # calculate some theoretical probabilities
        pmf, cdf = this_box.multivariate_probs(targets)

        fig, ax = plt.subplots(1, 2, sharex=True, tight_layout=True)
        hist, bins, patches = ax[0].hist(results, bins=range(1, this_box.template['packs_total'] + 2), density=True)
        cumulative, bins2, patches2 = ax[1].hist(results, bins=bins,
                                                 cumulative=True, density=True, histtype='step',
                                                 label='Simulated')
        ax[1].plot(bins[:-1], cdf, 'k--', label='Theoretical')
        ax[0].plot(bins[:-1], pmf, 'k--', label='Theoretical')
        
        flike = io.BytesIO()
        fig.savefig(flike)
        b64 = base64.b64encode(flike.getvalue()).decode()

        return self.render_to_response({
          'data': self.request.session,
          'result': results,
          'chart': b64
        })
