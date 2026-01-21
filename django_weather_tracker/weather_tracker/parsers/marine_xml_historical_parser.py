from weather_tracker.parsers.generic_parser import GenericParser


class MarineXmlHistoricalParser(GenericParser):

    def parse(self, raw_data: dict):

        report_list = self.parse_file_and_create_reports(raw_data)

        return report_list

    def parse_file_and_create_reports(self, raw_data: dict):
        marine_data = raw_data.get("marineData")

        # determine type, filter to only lake superior east/west?
        sub_region = marine_data["area"]["@subRegion"]

        report_list = []

        return report_list
