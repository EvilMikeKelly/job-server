import { Form, Formik } from "formik";
import { useNavigate } from "react-router-dom";
import * as Yup from "yup";
import { Button } from "../components/Button";
import CodelistBuilder from "../components/CodelistBuilder";
import FormDebug from "../components/FormDebug";
import { builderTimeEvents, builderTimeScales } from "../data/form-fields";
import { codelistSchema } from "../data/schema";
import { useFormStore } from "../stores";
import { FormDataTypes } from "../types";
import { requiredLoader } from "../utils";

export const QueryBuilderLoader = () =>
  requiredLoader({
    fields: ["codelist0", "codelist1", "frequency"],
  });

const validationSchema = Yup.object().shape({
  codelistA: codelistSchema(),
  codelistB: codelistSchema(),
  timeValue: Yup.number().required(),
  timeScale: Yup.string()
    .oneOf(builderTimeScales.map((event) => event.value))
    .required(),
  timeEvent: Yup.string()
    .oneOf(builderTimeEvents.map((event) => event.value))
    .required(),
});

function QueryBuilder() {
  const navigate = useNavigate();
  const formData: FormDataTypes = useFormStore((state) => state.formData);

  return (
    <Formik
      initialValues={{
        codelistA: formData.codelistA || formData.codelist0,
        codelistB: formData.codelistB || formData.codelist1,
        timeValue: formData.timeValue || 3,
        timeScale: formData.timeScale || "weeks",
        timeEvent: formData.timeEvent || "before",
      }}
      onSubmit={(values, actions) => {
        actions.validateForm().then(() => {
          useFormStore.setState({ formData: { ...formData, ...values } });
          return navigate("/preview-request");
        });
      }}
      validateOnMount
      validationSchema={validationSchema}
    >
      {({ isValid }) => (
        <Form>
          <h2 className="text-3xl font-bold mb-3">Report request</h2>
          <CodelistBuilder />
          <Button className="mt-6" disabled={!isValid} type="submit">
            Next
          </Button>

          <FormDebug />
        </Form>
      )}
    </Formik>
  );
}

export default QueryBuilder;
