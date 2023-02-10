import { Form, Formik } from "formik";
import { useLocation, Redirect } from "wouter";
import * as Yup from "yup";
import { AlertForm } from "../components/Alert";
import { Button } from "../components/Button";
import Checkbox from "../components/Checkbox";
import Fieldset from "../components/Fieldset";
import InputError from "../components/InputError";
import RadioButton from "../components/RadioButton";
import { demographics, filterPopulation } from "../data/form-fields";
import { useFormStore } from "../stores";
import { FormDataTypes } from "../types";
import { requiredLoader } from "../utils";

function FilterRequest() {
  const [, navigate] = useLocation();
  const formData: FormDataTypes = useFormStore((state) => state.formData);

  if (
    requiredLoader({
      fields: ["codelist0", "frequency"],
    })
  ) {
    return <Redirect to="" />;
  }

  const validationSchema = Yup.object().shape({
    filterPopulation: Yup.string()
      .oneOf(filterPopulation.items.map((item) => item.value))
      .required("Select a filter for the population"),
    demographics: Yup.array()
      .of(Yup.string().oneOf(demographics.items.map((item) => item.value)))
      .min(1)
      .max(demographics.items.length)
      .required(),
  });

  const initialValues = {
    filterPopulation: formData.filterPopulation || "",
    demographics: formData.demographics || [],
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, actions) => {
        actions.validateForm().then(() => {
          useFormStore.setState({ formData: { ...formData, ...values } });
          navigate("review-request");
        });
      }}
      validateOnMount
      validationSchema={validationSchema}
    >
      {({ errors, isValid, touched }) => (
        <Form className="flex flex-col gap-y-8">
          <AlertForm />
          <h1 className="text-4xl font-bold">Set report filters</h1>

          <Fieldset legend={filterPopulation.label}>
            {filterPopulation.items.map((item) => (
              <RadioButton
                key={item.value}
                id={item.value}
                label={item.label}
                name="filterPopulation"
                value={item.value}
              />
            ))}
            {errors.filterPopulation && touched.filterPopulation ? (
              <InputError>{errors.filterPopulation}</InputError>
            ) : null}
          </Fieldset>

          <Fieldset legend={demographics.label}>
            {demographics.items.map((item) => (
              <Checkbox
                key={item.value}
                id={item.value}
                label={item.label}
                name="demographics"
                value={item.value}
              />
            ))}
            {errors.demographics && touched.demographics ? (
              <InputError>Select one or more demographics</InputError>
            ) : null}
          </Fieldset>

          <div className="flex flex-row w-full gap-2 mt-10">
            <Button className="mt-6" disabled={!isValid} type="submit">
              Next
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
}

export default FilterRequest;
