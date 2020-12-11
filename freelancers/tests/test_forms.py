from django.test import TestCase
from freelancers.forms import ProposalForm


class TestProposalForm(TestCase):
    def test_day_less_than_one(self):
        form = ProposalForm(data={
            "task_id": 1,
            "rate": 30,
            "days": 0,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form['days'].errors, ["Days is greater then 1", ])

    def test_day_greater_than_one(self):
        form = ProposalForm(data={
            "task_id": 1,
            "rate": 30,
            "days": 1,
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form['days'].value(), 1)
