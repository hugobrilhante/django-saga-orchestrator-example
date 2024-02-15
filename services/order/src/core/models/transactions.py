from django.db import models

style = {
    'borderRadius': '50%',
    'width': '3.5rem',
    'height': '3.5rem',
    'display': 'flex',
    'justifyContent': 'center',
    'alignItems': 'center',
    'fontSize': '0.5rem',
    'fontWeight': 700,
    'background': '#6C757D',
    'color': 'white',
}

labels = ['order', 'stock', 'payment']


def create_initial_nodes():
    initial_nodes = []
    for i in range(len(labels)):
        _id = str(i + 1)
        node = dict(
            **{
                'id': _id,
                'position': {'x': 180 + i * 250, 'y': 100},
                'data': {'label': labels[i]},
                'style': dict(**style),
                'type': 'input' if _id == '1' else 'output' if _id == '3' else 'default',
                'sourcePosition': 'right',
                'targetPosition': 'left',
            }
        )
        initial_nodes.append(node)
    return list(initial_nodes)


class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, unique=True)
    nodes = models.JSONField(default=create_initial_nodes)
    logs = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.transaction_id)
