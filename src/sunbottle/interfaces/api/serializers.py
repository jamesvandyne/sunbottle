from rest_framework import serializers


class NormalizedDecimalField(serializers.DecimalField):
    def validate_precision(self, value):
        return value


class LineGraphDataset(serializers.Serializer):
    label = serializers.CharField(required=True)
    data = serializers.ListSerializer(child=NormalizedDecimalField(max_digits=10, decimal_places=3), required=True)


class LineGraphData(serializers.Serializer):
    labels = serializers.ListSerializer(child=serializers.CharField(allow_blank=True))
    yesterday = LineGraphDataset()
    today = LineGraphDataset()


class LineGraph(serializers.Serializer):
    data = LineGraphData(required=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["type"] = serializers.CharField(default="line")


class GenerationSummary(serializers.Serializer):
    total_generation = NormalizedDecimalField(max_digits=10, decimal_places=3, required=True)
    today_generation = NormalizedDecimalField(max_digits=10, decimal_places=3, required=True)
